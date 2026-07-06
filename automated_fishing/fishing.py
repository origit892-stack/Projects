from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import pyautogui
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Config:
    monitor_region: tuple[int, int, int, int] = (500, 760, 930, 145)
    prompt_region: tuple[int, int, int, int] | None = (860, 420, 230, 150)
    prompt_rgb: tuple[int, int, int] = (255, 160, 154)
    prompt_tolerance: int = 65
    min_prompt_pixels: int = 35
    max_prompt_pixels: int = 45000
    prompt_confirmations: int = 1
    post_cast_prompt_delay: float = 0.65
    use_ocr: bool = False
    ocr_scan_interval: float = 0.45
    debug_prompt: bool = True
    debug_prompt_interval: float = 3.0
    minigame_duration: float = 8.0
    minigame_margin: int = 28
    catch_goal_before_bait: int = 10
    # Leave as None to keep using the currently selected inventory slot.
    # Set to "5" only if you want the bot to force-select the rod.
    rod_slot: str | None = None
    bait_button: tuple[int, int] = (1485, 590)
    basic_bait_button: tuple[int, int] = (1485, 528)
    craft_button: tuple[int, int] = (960, 695)


CONFIG = Config()
RETINA_SCALE = 1.0
OCR_READER = None
OCR_IMPORT_FAILED = False
LAST_PROMPT_DEBUG = 0.0

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.02


def first_existing(*names: str) -> Path | None:
    for name in names:
        path = BASE_DIR / name
        if path.exists():
            return path
    return None


CRAFT_IMG = first_existing("craft_button.png")
FISH_IMG = first_existing("blue_fish.png", "fish.png", "Screenshot 2026-06-27 at 10.58.14.png")
CHEST_IMG = first_existing("chest.png", "treasure_chest.png", "Screenshot 2026-06-27 at 11.09.35.png")


def pil_to_rgb_array(image: Image.Image) -> np.ndarray:
    return np.array(image.convert("RGB"))


def get_retina_scale() -> float:
    screen_w, screen_h = pyautogui.size()
    shot = pyautogui.screenshot()
    scale_x = shot.size[0] / max(1, screen_w)
    scale_y = shot.size[1] / max(1, screen_h)
    scale = max(scale_x, scale_y)
    if 1.75 <= scale <= 2.25:
        return 2.0
    return 1.0


def capture_region(region: tuple[int, int, int, int] | None = None) -> tuple[Image.Image, np.ndarray, float]:
    if region is None:
        shot = pyautogui.screenshot()
        screen_w, _screen_h = pyautogui.size()
        scale = shot.size[0] / max(1, screen_w)
        if not 0.75 <= scale <= 2.25:
            scale = RETINA_SCALE
        return shot, pil_to_rgb_array(shot), scale

    shot = pyautogui.screenshot(region=region)
    scale = shot.size[0] / max(1, region[2])
    if not 0.75 <= scale <= 2.25:
        scale = RETINA_SCALE
    return shot, pil_to_rgb_array(shot), scale


def ensure_ocr_reader():
    global OCR_READER, OCR_IMPORT_FAILED
    if not CONFIG.use_ocr:
        return None
    if OCR_READER is not None:
        return OCR_READER
    if OCR_IMPORT_FAILED:
        return None

    print("[i] טוען EasyOCR בפעם הראשונה. זה יכול לקחת רגע...")
    try:
        import easyocr

        OCR_READER = easyocr.Reader(["en"], gpu=False, verbose=False)
    except Exception as exc:
        print(f"[-] EasyOCR נכשל, ממשיך עם זיהוי צבע/תמונה בלבד: {exc}")
        OCR_IMPORT_FAILED = True
        OCR_READER = None
    return OCR_READER


def quick_click(hold: float = 0.05) -> None:
    pyautogui.mouseDown()
    time.sleep(hold)
    pyautogui.mouseUp()


def click_burst(count: int = 2, hold: float = 0.045, gap: float = 0.055) -> None:
    for _ in range(count):
        quick_click(hold=hold)
        time.sleep(gap)


def release_inputs() -> None:
    pyautogui.mouseUp()
    for key in ("a", "d", "e", "space", "enter"):
        pyautogui.keyUp(key)


def press_key(key: str, delay: float = 0.25) -> None:
    pyautogui.press(key)
    time.sleep(delay)


def hold_key(key: str, seconds: float) -> None:
    pyautogui.keyDown(key)
    time.sleep(seconds)
    pyautogui.keyUp(key)


def actual_point_from_screenshot_point(x: float, y: float, scale: float) -> tuple[int, int]:
    return int(x / scale), int(y / scale)


def match_template(screen_rgb: np.ndarray, template_path: Path | None, threshold: float = 0.60):
    if template_path is None:
        return None
    try:
        template_rgb = pil_to_rgb_array(Image.open(template_path))
    except Exception:
        return None
    if float(np.std(template_rgb)) < 2.0:
        return None
    sh, sw = screen_rgb.shape[:2]
    th, tw = template_rgb.shape[:2]
    if th > sh or tw > sw:
        return None

    result = cv2.matchTemplate(screen_rgb, template_rgb, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val < threshold:
        return None
    x, y = max_loc
    return x, y, tw, th, float(max_val)


def prompt_masks(screen_rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    target = np.array(CONFIG.prompt_rgb, dtype=np.int16)
    diff = np.abs(screen_rgb.astype(np.int16) - target)
    rgb_mask = np.all(diff <= CONFIG.prompt_tolerance, axis=2)

    hsv = cv2.cvtColor(screen_rgb, cv2.COLOR_RGB2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    r = screen_rgb[:, :, 0]
    g = screen_rgb[:, :, 1]
    b = screen_rgb[:, :, 2]

    # Broad salmon/pink detector. OpenCV hue is 0-179; salmon is near red.
    hsv_mask = (
        ((hue <= 12) | (hue >= 165))
        & (sat >= 35)
        & (val >= 130)
        & (r >= 170)
        & (g >= 80)
        & (b >= 80)
        & (r >= g + 18)
    )

    rgb_mask = cv2.morphologyEx(rgb_mask.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    hsv_mask = cv2.morphologyEx(hsv_mask.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    return rgb_mask, hsv_mask


def mask_has_prompt(mask: np.ndarray) -> bool:
    count, _, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    for idx in range(1, count):
        _x, _y, w, h, area = stats[idx]
        if area < CONFIG.min_prompt_pixels or area > CONFIG.max_prompt_pixels:
            continue
        if w < 4 or h < 8:
            continue
        aspect = w / max(1, h)
        if 0.12 <= aspect <= 4.0:
            return True
    return False

    
def prompt_debug_stats(mask: np.ndarray) -> tuple[int, int, tuple[int, int, int, int] | None]:
    count, _, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    total = int(np.count_nonzero(mask))
    best_area = 0
    best_box = None
    for idx in range(1, count):
        x, y, w, h, area = stats[idx]
        if area > best_area:
            best_area = int(area)
            best_box = (int(x), int(y), int(w), int(h))
    return total, best_area, best_box


def detect_prompt_by_color(screen_rgb: np.ndarray) -> bool:
    rgb_mask, hsv_mask = prompt_masks(screen_rgb)
    return mask_has_prompt(rgb_mask) or mask_has_prompt(hsv_mask)


def find_minigame_target(screen_rgb: np.ndarray):
    fish = match_template(screen_rgb, FISH_IMG, threshold=0.55)
    if fish is not None:
        return fish

    chest = match_template(screen_rgb, CHEST_IMG, threshold=0.55)
    if chest is not None:
        return chest

    r = screen_rgb[:, :, 0]
    g = screen_rgb[:, :, 1]
    b = screen_rgb[:, :, 2]
    blue_mask = ((b > 120) & (g > 65) & (r < 100) & (b > r + 45)).astype(np.uint8)
    count, _, stats, _ = cv2.connectedComponentsWithStats(blue_mask, 8)
    best = None
    best_area = 0
    for idx in range(1, count):
        x, y, w, h, area = stats[idx]
        if 40 <= area <= 12000 and area > best_area and w >= 6 and h >= 6:
            best = (int(x), int(y), int(w), int(h), 1.0)
            best_area = int(area)
    return best


def largest_component_box(mask: np.ndarray, min_area: int, max_area: int | None = None):
    count, _, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    best = None
    best_area = 0
    for idx in range(1, count):
        x, y, w, h, area = stats[idx]
        if area < min_area:
            continue
        if max_area is not None and area > max_area:
            continue
        if area > best_area:
            best = (int(x), int(y), int(w), int(h), int(area))
            best_area = int(area)
    return best


def find_green_control(screen_rgb: np.ndarray):
    r = screen_rgb[:, :, 0]
    g = screen_rgb[:, :, 1]
    b = screen_rgb[:, :, 2]
    green_mask = (
        (g > 95)
        & (r > 45)
        & (r < 130)
        & (b > 45)
        & (b < 130)
        & (g > r + 18)
        & (g > b + 18)
    )
    maxc = screen_rgb.max(axis=2)
    minc = screen_rgb.min(axis=2)
    gray_mask = (
        (maxc - minc < 35)
        & (r > 70)
        & (r < 170)
        & (g > 70)
        & (g < 170)
        & (b > 70)
        & (b < 170)
    )
    mask = green_mask | gray_mask
    count, _, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    best = None
    best_area = 0
    for idx in range(1, count):
        x, y, w, h, area = stats[idx]
        # Ignore the thin bottom progress line; the control box is tall.
        if area < 500 or h < 25 or w < 35:
            continue
        if area > best_area:
            best = (int(x), int(y), int(w), int(h), int(area))
            best_area = int(area)
    return best


def find_blue_fish(screen_rgb: np.ndarray):
    template = match_template(screen_rgb, FISH_IMG, threshold=0.52)
    if template is not None:
        x, y, w, h, score = template
        # The tiny 4x3 template marks part of the fish; expand to a practical box.
        return int(x - 20), int(y - 20), 70, 55, score

    r = screen_rgb[:, :, 0]
    g = screen_rgb[:, :, 1]
    b = screen_rgb[:, :, 2]
    mask = (
        (b > 120)
        & (g > 65)
        & (r < 90)
        & (b > r + 45)
        & (b > g + 10)
    )
    return largest_component_box(mask, min_area=80, max_area=8000)


def detect_prompt_by_ocr(image: Image.Image) -> bool:
    reader = ensure_ocr_reader()
    if reader is None:
        return False
    try:
        results = reader.readtext(pil_to_rgb_array(image), detail=1, paragraph=False)
    except Exception as exc:
        print(f"[-] OCR נכשל בסריקת ביס: {exc}")
        return False

    for _bbox, text, prob in results:
        clean = text.strip().lower()
        if prob < 0.15:
            continue
        if "!" in clean or clean in {"i", "l", "1", "|"}:
            return True
    return False


def wait_for_prompt(now: float, last_ocr_scan: float) -> tuple[bool, float]:
    global LAST_PROMPT_DEBUG
    image, screen_rgb, _scale = capture_region(CONFIG.prompt_region)
    rgb_mask, hsv_mask = prompt_masks(screen_rgb)
    if mask_has_prompt(rgb_mask) or mask_has_prompt(hsv_mask):
        return True, last_ocr_scan

    if CONFIG.debug_prompt and now - LAST_PROMPT_DEBUG >= CONFIG.debug_prompt_interval:
        rgb_total, rgb_best, rgb_box = prompt_debug_stats(rgb_mask)
        hsv_total, hsv_best, hsv_box = prompt_debug_stats(hsv_mask)
        print(
            "[debug] no prompt | "
            f"rgb pixels={rgb_total} best={rgb_best} box={rgb_box} | "
            f"hsv pixels={hsv_total} best={hsv_best} box={hsv_box}"
        )
        try:
            image.save(BASE_DIR / "debug_prompt_latest.png")
        except Exception:
            pass
        LAST_PROMPT_DEBUG = now

    if CONFIG.use_ocr and now - last_ocr_scan >= CONFIG.ocr_scan_interval:
        return detect_prompt_by_ocr(image), now
    return False, last_ocr_scan


def cast_rod_properly() -> None:
    print("[+] זורק חכה...")
    release_inputs()
    time.sleep(0.25)
    if CONFIG.rod_slot:
        press_key(CONFIG.rod_slot, 0.25)
    screen_w, screen_h = pyautogui.size()
    pyautogui.moveTo(screen_w // 2, screen_h // 2, duration=0.05)
    time.sleep(0.35)

    pyautogui.mouseDown()
    time.sleep(0.5)
    pyautogui.mouseUp()
    time.sleep(0.3)

    pyautogui.mouseDown()
    time.sleep(0.1)
    pyautogui.mouseUp()
    release_inputs()
    print("[+] החכה במים. מחכה לסימן קריאה...")


def run_timed_minigame() -> None:
    print("[i] מנהל מיני-משחק לפי דג כחול ומד ירוק...")
    start = time.time()
    last_seen_ui = time.time()
    mouse_is_down = False
    while time.time() - start < CONFIG.minigame_duration:
        _image, screen_rgb, _scale = capture_region(CONFIG.monitor_region)
        green = find_green_control(screen_rgb)
        fish = find_blue_fish(screen_rgb)
        now = time.time()

        if green is not None and fish is not None:
            gx, _gy, gw, _gh, _ga = green
            fx, _fy, fw, _fh, _fa = fish
            green_center = gx + gw / 2
            fish_center = fx + fw / 2
            last_seen_ui = now

            if fish_center > green_center + CONFIG.minigame_margin:
                if not mouse_is_down:
                    pyautogui.mouseDown()
                    mouse_is_down = True
            elif fish_center < green_center - CONFIG.minigame_margin:
                if mouse_is_down:
                    pyautogui.mouseUp()
                    mouse_is_down = False
            else:
                if mouse_is_down:
                    pyautogui.mouseUp()
                    mouse_is_down = False
                quick_click(hold=0.035)
            time.sleep(0.025)
            continue

        if green is not None or fish is not None:
            last_seen_ui = now

        # If the minigame UI disappeared after being seen, the catch probably ended.
        if now - last_seen_ui > 0.7 and now - start > 2.0:
            break

        if mouse_is_down:
            pyautogui.mouseUp()
            mouse_is_down = False
        quick_click(hold=0.055)
        time.sleep(0.055)
    if mouse_is_down:
        pyautogui.mouseUp()
    release_inputs()


def clear_catch_popup() -> None:
    print("[+] מנקה חלון תפיסה...")
    release_inputs()
    time.sleep(0.45)
    press_key("space", 0.1)
    press_key("space", 0.1)
    release_inputs()
    time.sleep(1.4)


def find_craft_with_ocr() -> tuple[int, int] | None:
    reader = ensure_ocr_reader()
    if reader is None:
        return None

    image, _screen_rgb, scale = capture_region(None)
    try:
        results = reader.readtext(pil_to_rgb_array(image), detail=1, paragraph=False)
    except Exception as exc:
        print(f"[-] OCR נכשל בחיפוש Craft: {exc}")
        return None

    for bbox, text, prob in results:
        if prob < 0.20 or "craft" not in text.lower():
            continue
        top_left, _top_right, bottom_right, _bottom_left = bbox
        center_x = (top_left[0] + bottom_right[0]) / 2
        center_y = (top_left[1] + bottom_right[1]) / 2
        return actual_point_from_screenshot_point(center_x, center_y, scale)
    return None


def find_craft_with_image() -> tuple[int, int] | None:
    image, screen_rgb, scale = capture_region(None)
    match = match_template(screen_rgb, CRAFT_IMG, threshold=0.55)
    if match is None:
        return None
    x, y, w, h, _score = match
    return actual_point_from_screenshot_point(x + w / 2, y + h / 2, scale)


def click_craft_button(times: int = 10) -> bool:
    print("[+] נמצא Craft. מייצר פיתיונות...")
    pyautogui.moveTo(CONFIG.craft_button[0], CONFIG.craft_button[1], duration=0.1)
    time.sleep(0.3)
    for _ in range(times):
        quick_click(hold=0.08)
        time.sleep(0.35)
    return True


def buy_more_bait() -> None:
    print("\n[!] 10 תפיסות הושלמו. מחדש פיתיונות מול Angler...")
    release_inputs()
    hold_key("a", 1.0)
    time.sleep(0.5)

    press_key("e", 1.5)
    pyautogui.click(*CONFIG.bait_button)
    time.sleep(0.7)
    pyautogui.click(*CONFIG.basic_bait_button)
    time.sleep(1.2)

    click_craft_button(times=10)

    for _ in range(3):
        press_key("escape", 0.3)
    hold_key("d", 1.0)
    time.sleep(0.8)
    if CONFIG.rod_slot:
        press_key(CONFIG.rod_slot, 1.0)


def main() -> None:
    global RETINA_SCALE
    RETINA_SCALE = get_retina_scale()

    print("=" * 58)
    print("Starting Blox Fruits Color Auto-Fish V9.1")
    print("Move mouse to the top-left corner to stop.")
    print(f"Retina scale detected: {RETINA_SCALE:g}x")
    print(f"OCR enabled: {CONFIG.use_ocr}")
    print("=" * 58)

    catch_counter = 0
    prompt_hits = 0
    last_ocr_scan = 0.0

    time.sleep(3)
    cast_rod_properly()
    next_prompt_at = time.time() + CONFIG.post_cast_prompt_delay

    while True:
        try:
            now = time.time()
            if now < next_prompt_at:
                prompt_hits = 0
                time.sleep(0.05)
                continue

            prompt_detected, last_ocr_scan = wait_for_prompt(now, last_ocr_scan)
            prompt_hits = prompt_hits + 1 if prompt_detected else 0

            if prompt_hits < CONFIG.prompt_confirmations:
                time.sleep(0.05)
                continue

            print("[+] סימן קריאה זוהה. מושך ומתחיל מיני-משחק...")
            prompt_hits = 0
            click_burst(count=2, hold=0.045, gap=0.06)
            time.sleep(0.22)

            run_timed_minigame()
            clear_catch_popup()
            release_inputs()

            catch_counter += 1
            print(f"[i] תפיסות מאז חידוש מלאי: {catch_counter}/{CONFIG.catch_goal_before_bait}")

            if catch_counter >= CONFIG.catch_goal_before_bait:
                buy_more_bait()
                catch_counter = 0

            time.sleep(0.7)
            cast_rod_properly()
            next_prompt_at = time.time() + CONFIG.post_cast_prompt_delay
            time.sleep(0.8)

        except pyautogui.FailSafeException:
            print("\n[!] נעצר: העכבר הגיע לפינה השמאלית העליונה.")
            break
        except KeyboardInterrupt:
            print("\n[!] נעצר ידנית עם Ctrl+C.")
            break
        except Exception as exc:
            print(f"[-] שגיאה כללית: {exc}")
            time.sleep(0.5)


if __name__ == "__main__":
    main()
