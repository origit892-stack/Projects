# Google Classroom Provider Research — Lumio Mission

- **Date of research / access:** 2026-11-11 (all URLs fetched this date)
- **Method:** public web_search + web_extract only. No logins, no credentials, no browser auth automation.
- **Rules followed:** every claim has source URL + access date + short quote (≤20 words); facts labeled VERIFIED (official docs), NOT VERIFIED (no source found), or UNLIKELY/UNRELIABLE (contradicted or low-quality source). Official Google docs (developers.google.com, support.google.com, knowledge.workspace.google.com) are distinguished from community/forum claims (StackOverflow, GitHub, third-party blogs).
- **Hebrew search:** performed ("Google Classroom תאריכי מסירה לוח שנה"; takeout terms) — no Hebrew-language sources beyond the official (multi-language) Google docs were found; official docs carry Hebrew versions but no additional facts.
- **Context assumed:** Lumio is a static JS student app, no backend; student uses their own Google account (possibly a school WFE account in Israel); today is 2026-11-11.

---

## Q1. REST endpoints (base `https://classroom.googleapis.com/v1/`)

### Findings

1. **Base URL verified.** All three methods are documented under `classroom.googleapis.com/v1/…`. VERIFIED (official).
2. **courses.list (student view):** `GET https://classroom.googleapis.com/v1/courses`. Query params: `studentId` (accepts `"me"` for the requesting user; must be empty if `teacherId` set), `teacherId`, `courseStates[]`, `pageSize`, `pageToken`, `previewVersion`. Response: `{ "courses": [Course], "nextPageToken" }`. A student token with `classroom.courses.readonly` returns the courses that user is permitted to view; `studentId=me` makes it explicit. VERIFIED (official).
3. **courseStates values:** REST reference documents `ACTIVE`, `ARCHIVED` (default state `PROVISIONED`); the official Google Python client docs list the default filter as `ACTIVE, ARCHIVED, PROVISIONED, DECLINED`. So a student **can** request archived courses by passing `courseStates=ARCHIVED` (plus ACTIVE). VERIFIED (official REST page + official client-lib docs). `PUBLIC` exists in the enum for public courses — NOT VERIFIED in this session (not needed for Lumio).
4. **courses.courseWork.list:** `GET https://classroom.googleapis.com/v1/courses/{courseId}/courseWork`. Query params: `courseWorkStates[]`, `orderBy` (supported fields `updateTime`, `dueDate`), `pageSize`, `pageToken`, `previewVersion`. "Course students may only view `PUBLISHED` course work." Response: `{ "courseWork": [CourseWork], "nextPageToken" }`. Requires one of `classroom.coursework.students(.readonly)` or `classroom.coursework.me(.readonly)`. VERIFIED (official).
5. **CourseWork fields carrying the data Lumio needs** (resource `courses.courseWork`, page last updated 2026-11-02):
   - `title` (≤3000 chars), `description` (≤30,000 chars), `state` (`PUBLISHED`/`DRAFT`/`DELETED`), `alternateLink` ("Only populated if `state` is `PUBLISHED`"), `dueDate` (`Date` object, UTC) + `dueTime` (`TimeOfDay`, UTC), `maxPoints` (0/unspecified = ungraded), `workType` (ASSIGNMENT / SHORT_ANSWER_QUESTION / MULTIPLE_CHOICE_QUESTION), `materials[]` (≤20), `topicId`, `gradeCategory`, `assignment.studentWorkFolder` ("only populated for course teachers and administrators"). VERIFIED (official).
   - **The CourseWork resource has NO grade field.** The grade lives on the student's submission (see 6). VERIFIED (by absence in the documented field list, official).
6. **courses.courseWork.studentSubmissions.list:** `GET https://classroom.googleapis.com/v1/courses/{courseId}/courseWork/{courseWorkId}/studentSubmissions` (page last updated 2026-06-10). Path: `courseId`, `courseWorkId` ("may be set to the string literal `\"-\"` to request student work for all course work in the specified course"). Query: `userId` (accepts `"me"`), `states[]` (`SubmissionState`: `NEW`, `CREATED`, `TURNED_IN`, `RETURNED`, `RECLAIMED_BY_STUDENT`), `late` (`LATE_ONLY`/`NOT_LATE_ONLY`), `pageSize`, `pageToken`. "Course students may only view their own work." Scopes: one of `classroom.coursework.students(.readonly)` or `classroom.coursework.me(.readonly)`. VERIFIED (official).
7. **StudentSubmission fields** (resource `courses.courseWork.studentSubmissions`): `courseId`, `courseWorkId`, `id`, `userId`, `creationTime`, `updateTime`, `state`, `late`, `draftGrade`, `assignedGrade`, `rubricId`, `draftRubricGrades`, `assignedRubricGrades` (rubric fields are Developer Preview), `alternateLink` ("Absolute link to the submission in the Classroom web UI"), `courseWorkType`, `submissionHistory[]`, `assignmentSubmission`/`shortAnswerSubmission`/`multipleChoiceSubmission`. VERIFIED (official).
8. **Does a student token see the grade? YES.** Official guide "Set & update grades" (last updated 2026-09-03): "`draftGrade` is a tentative grade visible only to teachers." and "`assignedGrade` is the grade reported to students." Also field docs: `draftGrade` — "This is only visible to and modifiable by course teachers."; `assignedGrade` — "This may be modified only by course teachers." (i.e., readable by students). Scope `classroom.coursework.me.readonly` is described as "View your coursework and grades in Google Classroom." VERIFIED (official).
   - **Verdict nuance:** the grade is NOT on `CourseWork`; Lumio must call `studentSubmissions.list` (with `courseWorkId="-"` and `userId="me"`) to get `assignedGrade` per item.

### Sources

| URL | Doc date | Quote (≤20 words) | Label |
|---|---|---|---|
| https://developers.google.com/workspace/classroom/reference/rest/v1/courses/list | not shown | `GET https://classroom.googleapis.com/v1/courses` | VERIFIED |
| same | not shown | "the string literal \"me\", indicating the requesting user" | VERIFIED |
| same | not shown | "Restricts returned courses to those in one of the specified states." | VERIFIED |
| https://developers.google.com/workspace/classroom/reference/rest/v1/courses.courseWork/list | not shown | "Course students may only view `PUBLISHED` course work." | VERIFIED |
| https://developers.google.com/workspace/classroom/reference/rest/v1/courses.courseWork | 2026-11-02 | "Optional date, in UTC, that submissions for this course work are due." (dueDate) | VERIFIED |
| same | 2026-11-02 | "Only populated if `state` is `PUBLISHED`." (alternateLink) | VERIFIED |
| https://developers.google.com/workspace/classroom/reference/rest/v1/courses.courseWork.studentSubmissions/list | 2026-06-10 | "Course students may only view their own work." | VERIFIED |
| https://developers.google.com/workspace/classroom/reference/rest/v1/courses.courseWork.studentSubmissions | not shown | "Optional grade. If unset, no grade was set." (assignedGrade) | VERIFIED |
| same | not shown | "This is only visible to and modifiable by course teachers." (draftGrade) | VERIFIED |
| https://developers.google.com/workspace/classroom/guides/classroom-api/manage-grades | 2026-09-03 | "`assignedGrade` is the grade reported to students." | VERIFIED |
| https://developers.google.com/workspace/classroom/reference/rest/v1/SubmissionState | 2025-04-17 | "`NEW` The student has never accessed this submission." | VERIFIED |
| https://developers.google.com/resources/api-libraries/documentation/classroom/v1/python/latest/classroom_v1.courses.html | not shown | "The default value is ACTIVE, ARCHIVED, PROVISIONED, DECLINED. (repeated)" | VERIFIED (official client-lib) |

### Verdict
**Q1:** All three endpoints exist exactly as assumed (base `https://classroom.googleapis.com/v1/`). Student view = `courses.list` with `studentId=me` (+ `courseStates` incl. `ARCHIVED`); `courseWork.list` per course (PUBLISHED only for students); `studentSubmissions.list` with `courseWorkId="-"` and `userId="me"` for all own submissions. A student token with `coursework.me.readonly` **does** see grades — via `StudentSubmission.assignedGrade` (not on CourseWork). **Confidence: high.**

---

## Q2. Minimal scopes; sensitivity/verification; K-12 restrictions

### Findings

1. **`classroom.courses.readonly`** = "View your Google Classroom classes." **`classroom.coursework.me.readonly`** = "View your coursework and grades in Google Classroom." (Official scope table, last updated 2026-09-03.) VERIFIED.
2. **No separate scope needed for grades:** `coursework.me.readonly` explicitly includes grades. There is also an alias scope `classroom.student-submissions.me.readonly` with the identical description ("View your coursework and grades…"); it is not required for Lumio. VERIFIED (official).
3. **These two scopes cover Lumio's full read needs:** courses (incl. state), published course work (dueDate/dueTime/description/title/alternateLink/maxPoints), own submissions (state/late/assignedGrade/alternateLink). VERIFIED (by combining official method-scopes lists: courses.list requires `courses(.readonly)`; coursework.list and studentSubmissions.list each accept `coursework.me.readonly`).
4. **Sensitive scopes / verification:** Official Classroom add-ons project-configuration doc: "Because Classroom scopes are Sensitive, you must request OAuth verification before launching your add-on." OAuth App Verification Help Center: "Apps that request access to scopes categorized as sensitive or restricted must complete Google's OAuth app verification before being granted access." An unverified external app gets the unverified-app screen and "the app will be subject to the 100-user cap." VERIFIED (official). Note: individual per-scope categories are shown in Cloud Console automatically; the official add-ons doc's blanket statement that Classroom scopes are sensitive is the strongest official statement found. (One third-party setup guide claims some classroom read scopes are "non sensitive" — UNRELIABLE/contradicted by the official doc above; treat as NOT VERIFIED.)
5. **K-12 / Workspace for Education:** Admin docs ("Control which apps access Google Workspace data", last updated 2026-10-26): admins can set per-app access to **Trusted / Limited / Specific Google data / Blocked** in Admin console → Security → Access and data control → API controls, and can restrict or unrestrict access per Google service. "For Google Workspace for Education, additional restrictions might prevent users in primary and secondary institutions from accessing certain apps." VERIFIED (official). Consequence: in an Israeli school WFE domain, the **school admin can block third-party apps from accessing Classroom data** (or any service), which would stop Lumio for that student regardless of consent. For personal Google accounts, no such admin gate exists.
   - Related but secondary: admins can also turn Classroom itself on/off per user (official support page "Control user access to Classroom"). VERIFIED (official).

### Sources

| URL | Doc date | Quote (≤20 words) | Label |
|---|---|---|---|
| https://developers.google.com/workspace/classroom/guides/auth | 2026-09-03 | "View your coursework and grades in Google Classroom." (coursework.me.readonly) | VERIFIED |
| same | 2026-09-03 | "View your Google Classroom classes." (courses.readonly) | VERIFIED |
| https://developers.google.com/workspace/classroom/add-ons/developer-guides/project-configuration | not shown | "Because Classroom scopes are Sensitive, you must request OAuth verification" | VERIFIED |
| https://support.google.com/cloud/answer/13463073 | not shown | "categorized as sensitive or restricted must complete Google's OAuth app verification" | VERIFIED |
| https://support.google.com/cloud/answer/13464018 | not shown | "the app will be subject to the 100-user cap" | VERIFIED |
| https://knowledge.workspace.google.com/admin/apps/control-which-apps-access-google-workspace-data | 2026-10-26 | "additional restrictions might prevent users in primary and secondary institutions from accessing certain apps" | VERIFIED |
| https://support.google.com/edu/classroom/answer/6023715 | not shown | "use the Google Admin console to give teachers and students access to Classroom" | VERIFIED |
| https://integrations.sadlierconnect.com/article/548 | n/a (third-party) | claims classroom.courses.readonly "non sensitive" | UNRELIABLE (contradicted by official) |

### Verdict
**Q2:** Minimal set = `https://www.googleapis.com/auth/classroom.courses.readonly` + `https://www.googleapis.com/auth/classroom.coursework.me.readonly`; the latter already covers grades — no third scope needed. Official docs state Classroom scopes are Sensitive, so a public app must pass OAuth app verification; until then it runs in Testing mode (see Q5). For school (WFE) accounts, the school admin can restrict or block the app per service — a real deployment risk for students. **Confidence: high** (scope coverage, sensitivity statement, admin control); per-scope console categorization NOT independently re-verified in Console.

---

## Q3. What a student's own token CAN and CANNOT read

### Findings

**Readable (VERIFIED, official method docs + scope docs):**
1. Own courses: `courses.list` (studentId=me; any state incl. `ARCHIVED` via `courseStates`). Course fields: name, section, description, room, `courseState`, `alternateLink`, `calendarId`, creation/update times, subject, levels.
2. Own published course work per course: `courseWork.list` — title, description (up to 30k chars), dueDate/dueTime (UTC), maxPoints, workType, materials (links/Drive/YouTube), topicId, alternateLink. Students see only PUBLISHED items ("Course students may only view `PUBLISHED` course work.").
3. Own submissions: `studentSubmissions.list` (userId="me", courseWorkId="-" for all in course) — state (NEW/CREATED/TURNED_IN/RETURNED/RECLAIMED_BY_STUDENT), late, **assignedGrade** ("the grade reported to students"), alternateLink to the submission, submission content (assignment attachments, short answer, multiple choice), submissionHistory.

**NOT readable (VERIFIED, official):**
1. Other students' work or grades: "Course students may only view their own work" (studentSubmissions.list); grade scopes are role-bound ("coursework.students*" is for teachers/admins only).
2. `draftGrade` on any submission: "This is only visible to and modifiable by course teachers."
3. Teacher/admin-only fields: Course.teacherFolder — "This field will only be set for teachers of the course and domain administrators."; CourseWork.assignment.studentWorkFolder — same.
4. DRAFT/DELETED course work (students only see PUBLISHED).
5. Class roster (classmates) requires an additional scope (`classroom.rosters(.readonly)`); it is not needed for Lumio's stated data and is **not** covered by the two minimal scopes. (Scope table: "View your Google Classroom class rosters.")

### Sources

| URL | Doc date | Quote (≤20 words) | Label |
|---|---|---|---|
| https://developers.google.com/workspace/classroom/reference/rest/v1/courses.courseWork.studentSubmissions/list | 2026-06-10 | "Course students may only view their own work." | VERIFIED |
| https://developers.google.com/workspace/classroom/reference/rest/v1/courses.courseWork.studentSubmissions | not shown | "This is only visible to and modifiable by course teachers." (draftGrade) | VERIFIED |
| https://developers.google.com/workspace/classroom/reference/rest/v1/courses | 2026-11-02 | "This field will only be set for teachers of the course and domain administrators." | VERIFIED |
| https://developers.google.com/workspace/classroom/reference/rest/v1/courses.courseWork/list | not shown | "Course students may only view `PUBLISHED` course work." | VERIFIED |
| https://developers.google.com/workspace/classroom/guides/auth | 2026-09-03 | "View your Google Classroom class rosters." (rosters.readonly) | VERIFIED |

### Verdict
**Q3:** With the student's own token: readable = own courses (incl. archived), published course work (due dates, descriptions, titles, links, max points), own submissions with grades/late state/links. Not readable = other students, other students' grades, draft grades, teacher-only Drive folders, draft/deleted work. **Confidence: high.**

---

## Q4. Real-time, rate limits, token lifetime, GSI flow

### Findings

1. **PUSH EXISTS — correction to the mission assumption.** The Classroom API has an official push-notifications feature built on **Cloud Pub/Sub** (NOT the generic Realtime API "channels"): "The Classroom API push notifications feature allows applications using the Classroom API to subscribe for notifications when data changes in Classroom." (Official guide, last updated 2026-09-03.) VERIFIED.
2. **Feeds:** three types; the one Lumio would use: per-course "course work changes for course" feed — "exposes notifications when any course work or student submission objects are created or modified in that course." VERIFIED (official).
3. **Hard requirements (block a pure static-JS app today):**
   - A Cloud Pub/Sub **topic + subscription** in a GCP project, with **billing enabled** ("Review the Cloud Pub/Sub pricing, and enable billing").
   - Grant the service account `classroom-notifications@system.gserviceaccount.com` publish permission on the topic.
   - A token with scope `https://www.googleapis.com/auth/classroom.push-notifications` plus the data scopes, and a retained OAuth grant ("For notifications to be delivered, the application must retain an OAuth grant").
   - "Your registration lasts a week, but you can extend it at any point before it expires."
   - A **server** to consume Pub/Sub (webhook or polling a subscription) — impossible from a browser-only static app.
   VERIFIED (official).
4. **WFE-domain caveat (critical for Israeli schools):** "Note: We are aware of an issue where notifications are not sent for changes in courses where the course owner is not part of a Google Workspace for Education domain." (English official guide.) Translated versions of the same page additionally note coursework-change notifications are not sent for non-WFE courses. So for a student on a plain consumer Google account (or a course owned by one), push may simply never fire. VERIFIED (official, English text for roster feed; coursework-feed wording VERIFIED via official translated versions of the same page).
5. **Latency:** "Notifications are delivered to a Cloud Pub/Sub topic, usually within a few minutes of the change." — i.e., near-real-time, not instant. VERIFIED (official).
6. **Rate limits (official "Usage Limits", last updated 2026-09-03):** quota checked on a 60-second moving average.
   - Queries per day per client: 4,000,000 (avg 46 QPS)
   - Queries per minute per client: 3,000 (50 QPS)
   - Queries per minute per user: 1,200 (20 QPS)
   VERIFIED (official). For one student polling a handful of courses, limits are a non-issue.
7. **GSI JS token flow returns ACCESS TOKENS ONLY — no refresh token.**
   - Official JS reference (`initTokenClient`): the `TokenResponse` type contains `access_token`, `expires_in`, `hd`, `prompt`, `token_type`, `scope`, `state`, `error*` — **no `refresh_token` field**. VERIFIED (official, https://developers.google.com/identity/oauth2/web/reference/js-reference).
   - "In the Token based authorization model, there is no need to store per-user refresh tokens on your backend server." (Official token-model guide, last updated 2026-05-26.) VERIFIED.
   - "For improved user security, this automatic token refresh process is not supported by the Google Identity Services library. Your web app must be updated to detect an expired access token and request a new one." (Official GSI migration guide.) VERIFIED.
   - Lifetime: official example token response shows `"expires_in": 3599` → **~1 hour** per access token. VERIFIED (official example).
   - Refresh = a **user gesture** required: "obtain a new token by calling `requestAccessToken()` from a user-driven event such as a button press." VERIFIED (official).
   - Corollary for Lumio: **background sync while the PC is off (or the tab closed) is impossible with the GSI-only flow.** The only silent re-token window is while the consent/grant is still valid and the app re-requests from a user gesture; with a server-side flow (authorization code + stored refresh token) or the (server-based) Pub/Sub push, background sync becomes possible.
   - In Testing mode, even grants expire: "Authorizations by a test user will expire seven days from the time of consent." (Official, see Q5.) VERIFIED.

### Sources

| URL | Doc date | Quote (≤20 words) | Label |
|---|---|---|---|
| https://developers.google.com/workspace/classroom/guides/push-notifications | 2026-09-03 | "subscribe for notifications when data changes in Classroom" | VERIFIED |
| same | 2026-09-03 | "notifications when any course work or student submission objects are created or modified" | VERIFIED |
| same | 2026-09-03 | "notifications are not sent for changes in courses where the course owner is not part of" (+ WFE domain) | VERIFIED |
| same | 2026-09-03 | "Notifications are delivered to a Cloud Pub/Sub topic, usually within a few minutes" | VERIFIED |
| same | 2026-09-03 | "Your registration lasts a week, but you can extend it" | VERIFIED |
| https://developers.google.com/workspace/classroom/reference/limits | 2026-09-03 | "Queries per minute per user \| 1,200 (20 QPS)" | VERIFIED |
| https://developers.google.com/identity/oauth2/web/reference/js-reference | not shown | TokenResponse: "access_token — The access token of a successful token response." (no refresh_token field) | VERIFIED |
| https://developers.google.com/identity/oauth2/web/guides/use-token-model | 2026-05-26 | "there is no need to store per-user refresh tokens on your backend server" | VERIFIED |
| https://developers.google.com/identity/oauth2/web/guides/migration-to-gis | not shown | "automatic token refresh process is not supported by the Google Identity Services library" | VERIFIED |
| same | not shown | `"expires_in": 3599` (sample GSI token response, no refresh_token) | VERIFIED |
| https://support.google.com/cloud/answer/15549945 | not shown | "Authorizations by a test user will expire seven days from the time of consent." | VERIFIED |

### Verdict
**Q4:** The "no push" assumption is **wrong** — Classroom has Pub/Sub push notifications (coursework-change feed), but they require a server + GCP Pub/Sub + billing + `classroom.push-notifications` scope, arrive "within a few minutes", expire after a week, and are unreliable for courses outside a WFE domain. Rate limits: ~46 QPS/client/day, 50 QPS/min, 20 QPS/user/min. GSI `initTokenClient` returns **access token only** (~1h, `expires_in` ≈ 3599), **no refresh token**, no automatic refresh, re-token needs a user gesture → **background sync while the PC is off is impossible with the current GSI-only architecture**. **Confidence: high (all official).**

---

## Q5. OAuth app lifecycle (Testing mode, verification, registration)

### Findings

1. **Testing mode (official, current OAuth platform docs):**
   - "Projects configured with a publishing status of **Testing** are limited to up to 100 test users listed in the OAuth consent screen." (support.google.com/cloud/answer/15549945, "Manage App Audience".) VERIFIED.
   - "Authorizations by a test user will expire seven days from the time of consent. If your OAuth client requests an `offline` access type and receives a refresh token, that token will also expire." VERIFIED.
   - Only test users on the allowlist can authorize (with a warning screen); the **only exception** is apps requesting only name/email/profile scopes. VERIFIED.
   - Production-readiness overview: "Only users explicitly added to the test user allowlist can access the app (limited to a hard cap of 100 test users)." Also: if a Workspace admin marks the app **Trusted**, it overrides "the 100-test-user cap and the 7-day refresh token expiration limit" for that org. VERIFIED (official, developers.google.com/identity/protocols/oauth2/production-readiness/overview).
   - Practical consequence for Lumio (GSI, no refresh token): in Testing mode the student's **authorization itself expires every 7 days**, so they'd be re-prompted at least weekly (worse: any token they hold dies; they must re-run the consent popup). VERIFIED (by combination of the two official quotes).
2. **When Production verification is required:** "Apps that request access to scopes categorized as sensitive or restricted must complete Google's OAuth app verification before being granted access." Non-sensitive-only apps skip verification (optional lighter "brand-verification" for logo/name). Since official docs classify Classroom scopes as Sensitive (Q2), a **published external Lumio app must complete OAuth app verification** (security assessment, demo video, data-access justification, etc.) before other users can use it; until then → unverified-app screen + 100-user cap. VERIFIED (official).
   - Nuance: Lumio's owner can **publish the app to Production without verification** and still use it personally (unverified warning; user can continue from a personal account — the "continue past the scary screen" behavior is community-observed, NOT VERIFIED in official text). The school admin may also mark the app Trusted/Limited/Blocked (Q2).
3. **What must be registered:**
   - Google Auth platform: **OAuth consent screen** (branding: app name, support email, logo; user type External; scopes = the two read scopes) — "You must configure the OAuth consent screen before you can create an OAuth client ID." (official, Classroom MCP setup doc.) VERIFIED.
   - **OAuth client (Web application)** with **Authorized JavaScript origins** = the page origins that load the GSI client (e.g. `https://<lumio-public-domain>` and `http://localhost:5173`). Official rules: "JavaScript origins must use the HTTPS scheme, not plain HTTP. Localhost URIs (including localhost IP address URIs) are exempt from this rule." → **`http://localhost:5173` is allowed.** VERIFIED (official, support.google.com/cloud/answer/15549257).
   - **Redirect URIs:** only needed for server-side authorization-code flows ("Applications that access Google APIs from a server … must specify authorized redirect URIs"); for the GSI implicit popup flow, the authorized **JavaScript origin** is what matters. If a redirect URI is added later for a backend flow: "Redirect URIs must use the HTTPS scheme, not plain HTTP. Localhost URIs … are exempt" and "For testing, you can specify URIs that refer to the local machine, such as `http://localhost:8080`." → `http://localhost:5173` as redirect URI also allowed. VERIFIED (official).
   - Changes to origins/redirect URIs can take "5 minutes to a few hours" to propagate. VERIFIED (official).

### Sources

| URL | Doc date | Quote (≤20 words) | Label |
|---|---|---|---|
| https://support.google.com/cloud/answer/15549945 | not shown | "publishing status of Testing are limited to up to 100 test users" | VERIFIED |
| same | not shown | "Authorizations by a test user will expire seven days from the time of consent." | VERIFIED |
| https://developers.google.com/identity/protocols/oauth2/production-readiness/overview | not shown | "Only users explicitly added to the test user allowlist can access the app" | VERIFIED |
| same | not shown | "overrides … the 100-test-user cap and the 7-day refresh token expiration limit" (Trusted apps) | VERIFIED |
| https://support.google.com/cloud/answer/13463073 | not shown | "sensitive or restricted must complete Google's OAuth app verification" | VERIFIED |
| https://developers.google.com/workspace/classroom/add-ons/developer-guides/project-configuration | not shown | "Because Classroom scopes are Sensitive, you must request OAuth verification" | VERIFIED |
| https://support.google.com/cloud/answer/15549257 | not shown | "JavaScript origins must use the HTTPS scheme … Localhost URIs … are exempt" | VERIFIED |
| https://developers.google.com/identity/protocols/oauth2/web-server | not shown | "you can specify URIs that refer to the local machine, such as http://localhost:8080" | VERIFIED |
| https://developers.google.com/workspace/classroom/guides/mcp/configure-mcp-server | not shown | "You must configure the OAuth consent screen before you can create an OAuth client ID." | VERIFIED |
| https://stackoverflow.com/questions/75725474 | n/a (community) | "you can still bypass that to authorize it" (unverified screen) | NOT VERIFIED (community) |

### Verdict
**Q5:** Testing mode = max **100 test users**, authorizations (and refresh tokens) **expire after 7 days**, test users only, warning screen. Production verification is **required to publish** because Classroom scopes are Sensitive (verification = security assessment + demo video + justification). Registration = OAuth consent screen (branding) + Web OAuth client with **Authorized JavaScript origins** (HTTPS; `http://localhost:5173` explicitly exempt/allowed) — GSI popup flow needs the JS origin, not a redirect URI. For a single-student Lumio, Testing mode with the student as a test user works but forces **weekly re-consent** unless the app is published/verified or the school admin marks it Trusted. **Confidence: high.**

---

## Q6. Can Lumio use the Classroom API WITHOUT creating its own OAuth client?

### Findings

1. **Official requirement: the app itself needs its own project + client.** "Any application that calls Google APIs needs to enable those APIs in the API Console." and "Any application that uses OAuth 2.0 to access Google APIs must have authorization credentials that identify the application to Google's OAuth 2.0 server." (Official web-server OAuth guide.) VERIFIED. Even Google's own new **Classroom MCP server** (remote, `classroommcp.googleapis.com`) documentation instructs: "You must configure the OAuth consent screen before you can create an OAuth client ID." — i.e., Google's recommended path is still *your own* client. VERIFIED (official).
2. **No official reseller/intermediary path found.** I found **no** Google document offering third-party "OAuth intermediaries" that would expose Classroom reads under *another* app's client ID. NOT VERIFIED that any such official path exists (absence of evidence across official docs).
3. **Why another app's client is not a valid substitute (officially supported reasoning):**
   - The OAuth client ID *is* the app's identity: "Think of your client ID like your app's unique username … This ID helps Google identify your app." (official.) If Lumio embeds a third party's client ID, **that third party's app** receives the consent grant and user data; Lumio's users are authorizing *their* app, not Lumio. The app owner controls what the token is used for and under whose privacy policy/verification the data flows.
   - For school accounts, the admin console surfaces the app's identity: apps are shown with "the full OAuth2 client ID of the app, the number of users, the privacy policy, and the support information" — the school would see the *intermediary's* app, not Lumio; a school that blocks unknown third-party apps (Q2) would block the intermediary's client. VERIFIED (official admin doc).
   - Google's OAuth policies require the app to be accurately identified on the consent screen; routing another app's client through a different product is a ToS/privacy violation of the user's expectation (the consent screen shows the client's owner). (Policy framing from official docs; the specific "no piggybacking" rule is a policy interpretation — NOT VERIFIED as a single citable sentence.)
   - Community "free access" schemes for other Google APIs (shared client IDs in open-source tools) are well-known ToS violations and are blocked/rotated — NOT VERIFIED as an official position, but UNLIKELY to be a durable option.
4. **What the user MUST do (official, free):**
   - Create a Google Cloud project (free), configure the OAuth consent screen (External user type; Testing initially; app name "Lumio", support email, logo, privacy policy URL).
   - Enable **Google Classroom API** in the project (`gcloud services enable classroom.googleapis.com` or console).
   - Create an OAuth 2.0 client ID of type **Web application** with Authorized JavaScript origin(s).
   - Cost: official Classroom prerequisites doc: "You don't need to use any paid Google Cloud features to use Classroom API." VERIFIED. (Pub/Sub push would add GCP usage; not needed for the MVP.)

### Sources

| URL | Doc date | Quote (≤20 words) | Label |
|---|---|---|---|
| https://developers.google.com/identity/protocols/oauth2/web-server | not shown | "Any application that calls Google APIs needs to enable those APIs in the API Console." | VERIFIED |
| same | not shown | "must have authorization credentials that identify the application to Google's OAuth 2.0 server" | VERIFIED |
| https://support.google.com/cloud/answer/15549257 | not shown | "Think of your client ID like your app's unique username" | VERIFIED |
| https://developers.google.com/workspace/classroom/guides/mcp/configure-mcp-server | not shown | "You must configure the OAuth consent screen before you can create an OAuth client ID." | VERIFIED |
| https://knowledge.workspace.google.com/admin/apps/control-which-apps-access-google-workspace-data | 2026-10-26 | "Shows the full OAuth2 client ID of the app, the number of users, the privacy policy" | VERIFIED |
| https://developers.google.com/workspace/classroom/guides/onboarding/prerequisites | not shown | "You don't need to use any paid Google Cloud features to use Classroom API." | VERIFIED |
| (no URL) | — | official reseller/intermediary path for Classroom reads | NOT VERIFIED (not found) |

### Verdict
**Q6:** No official reseller/intermediary path exists that would let Lumio read under someone else's client; using another app's OAuth client would mean *their* app/privacy policy/verification stands behind the data (and school admins would see their app, not Lumio) — unacceptable as "Lumio's" integration. The user **must** create their own (free) GCP project + consent screen + Classroom API + Web OAuth client. **Confidence: high** for the requirement and cost; the "no intermediary exists" point is absence-of-evidence (NOT VERIFIED that one exists, but nothing official suggests it does).

---

## Q7. No-API alternatives

### (a) Google Takeout for Classroom

**Findings:**
1. **Official support page "Export your data from Google Classroom"** (support.google.com/edu/classroom/answer/10204459): "You can export and download your data from Classroom. You can download data that hasn't been deleted." VERIFIED.
2. **Exact student datasets (official list):** "For Students: — Student posts. — Student submissions and associated comments, grades, and rubrics. — Student practice sets and associated grades." VERIFIED. (Read Along + Classroom Analytics items are "domain wide takeout only" — i.e., school-admin exports, not the student's own takeout.)
   - **What's notably absent from the student list:** structured **course information** (title, description, room, **due dates**) appears only under "For Teachers and co-teachers". Whether student-side JSON files embed course/assignment metadata (titles/due dates) is NOT VERIFIED — the official page does not document the student export schema.
   - Third-party tool `classroom-export-viewer` (GitHub, community) describes Takeout Classroom data as "JSON exports" and notes "Google does not include announcements or standalone materials in Google Classroom exports." — community evidence, NOT VERIFIED officially.
3. **One-shot, user-initiated only (no auto feed):** Takeout offers "One-time archive" and "Scheduled exports — Automatically create an archive … every 2 months for one year … Note: … To use this option, make sure Google Photos is the only product selected for your export." (support.google.com/accounts/answer/3024190.) → **Scheduled Takeout is Photos-only; Classroom exports are manual one-shot archives.** VERIFIED (official).
4. **Work/school account caveat:** "If you use a work or school account, some data might not be available for download." VERIFIED (official) — school policy can shrink what a student can export.
5. **Format:** archive is a ZIP of product folders; Classroom content as JSON files (community-verified; official page doesn't spell out JSON for Classroom). Archives expire in ~7 days, max 5 downloads.

### (b) Google Calendar

**Findings:**
1. **Yes — Classroom due dates DO appear in the student's Google Calendar.** Official student help page "View due dates and events in a calendar" (support.google.com/edu/classroom/answer/6272985): "For each class, you share a Classroom calendar and a Google Calendar with your teacher and classmates. **Only items with due dates appear in these calendars.**" and "In your Google Calendar, you can find all your class calendars." VERIFIED (official).
   - Also confirmed at the API level: `Course.calendarId` — "a calendar that all course members can see, to which Classroom adds events for course work and announcements in the course" (created when the course becomes ACTIVE). VERIFIED (official REST).
   - Admin can disable: "If you can't access Google Calendar, your Google Workspace administrator might have turned it off for your account." VERIFIED (official).
2. **ICS export/subscription:** "Export events from your Google Calendar" (support.google.com/calendar/answer/37111): "The exported file is an .ics file, which you can import into other calendar apps." — export all calendars (Settings → Import & export → Export, ZIP of .ics) or a single calendar (Settings and sharing → Export calendar). "You must have the 'Make changes and manage sharing' permission for the calendar you wish to export." and "If you use a Google Calendar through work, school, or another organization, your administrator may restrict export settings." A per-calendar iCal feed ("Public/Secret address in iCal format") also exists (referenced on the same page). VERIFIED (official).
   - Whether a **student** holds the "Make changes and manage sharing" permission on the auto-created class calendar is NOT directly documented (they can add personal reminders to the class calendar per the Classroom help page, which suggests edit-ish rights) — INFERRED, mark NOT VERIFIED. If blocked, a calendar read via the Calendar API (course `calendarId`) is the programmatic fallback — calendar.readonly is non-sensitive, but it still needs the same GCP OAuth client as the rest of Lumio.
3. **What the calendar contains / is missing (for Lumio's use):**
   - Includes: one calendar event per **course-work item that has a due date** (+ announcements also appear as events on the course calendar per the `calendarId` doc) — title = the classwork item, on its due date.
   - Missing: items **without due dates** ("Only items with due dates appear"), **grades** (never), **assignment descriptions** (event body content is not documented — NOT VERIFIED whether descriptions are embedded), course metadata (course name appears as the calendar name; section/description not documented).
   - It is a **snapshot feed**: events exist in Calendar live, but there is no Classroom→Calendar API subscription for the browser; the student must export ICS manually (one-shot) or use the Calendar API.

### Sources

| URL | Doc date | Quote (≤20 words) | Label |
|---|---|---|---|
| https://support.google.com/edu/classroom/answer/10204459 | not shown | "For Students: — Student posts. — Student submissions and associated comments, grades, and rubrics." | VERIFIED |
| same | not shown | "If you use a work or school account, some data might not be available for download." | VERIFIED |
| https://support.google.com/accounts/answer/3024190 | not shown | "make sure Google Photos is the only product selected for your export" (scheduled exports) | VERIFIED |
| https://github.com/psvenk/classroom-export-viewer | n/a (community) | "viewing JSON exports (from Google Takeout) of Google Classroom data" | NOT VERIFIED (community) |
| https://support.google.com/edu/classroom/answer/6272985 | not shown | "Only items with due dates appear in these calendars." | VERIFIED |
| same | not shown | "In your Google Calendar, you can find all your class calendars." | VERIFIED |
| https://developers.google.com/workspace/classroom/reference/rest/v1/courses | 2026-11-02 | "to which Classroom adds events for course work and announcements in the course" (calendarId) | VERIFIED |
| https://support.google.com/calendar/answer/37111 | not shown | "The exported file is an .ics file, which you can import into other calendar apps." | VERIFIED |
| same | not shown | "You must have the 'Make changes and manage sharing' permission for the calendar you wish to export." | VERIFIED |
| same | not shown | "your administrator may restrict export settings" | VERIFIED |
| (student export permission on class calendar) | — | — | NOT VERIFIED (inferred) |

### Verdict
**Q7:** (a) Takeout: real and official — student exports contain **student posts + own submissions with grades/comments/rubrics + practice sets** (ZIP/JSON), but **no documented course info/due dates for students**, no announcements/materials (community), work/school accounts may be restricted, and it is **strictly one-shot, user-initiated** (scheduled exports are Photos-only) — no auto feed. (b) Calendar: **yes**, each class has a Google Calendar visible to the student containing **due-date items only** (plus announcements per API doc); students can export **ICS** from Calendar settings if they have edit permission on that shared calendar (admin may restrict; student permission NOT VERIFIED). Missing from calendar: no-due-date work, grades, (undocumented) descriptions. **Confidence: high** for existence/limits; medium for the ICS-permission and student-export-schema details.

---

## Q8. Pagination / limits

### Findings

1. **No official per-page maximum is documented** for `courses.list`, `courseWork.list`, or `studentSubmissions.list`: "Maximum number of items to return. Zero or unspecified indicates that the server may assign a maximum. The server may return fewer than the specified number of results." VERIFIED (official, all three method pages).
2. **Roster endpoints:** `courses.students.list` — "The default is 30 if unspecified or 0." (official). Community reports suggest 30 is also the effective **cap** for students/teachers lists ("if you're setting a value higher than 30 and still returning only 30, chances are that's the maximum value … doesn't seem to be documented") — NOT VERIFIED (community).
3. **Observed cap for courses.list:** a StackOverflow thread titled "I get always 500 items when list Classroom" (community) indicates the server caps `courses.list` pages at ~**500** items when no/large `pageSize` is given — NOT VERIFIED (community; no official number).
4. **Practical guidance (safe):** request with `pageSize` (e.g. 100), always follow `nextPageToken` until empty, and tolerate "fewer than requested" pages. Real-world student course counts (dozens) fit in 1–2 pages; the per-user 20 QPS limit (Q4) is the binding constraint only in pathological cases.

### Sources

| URL | Doc date | Quote (≤20 words) | Label |
|---|---|---|---|
| https://developers.google.com/workspace/classroom/reference/rest/v1/courses/list | not shown | "Zero or unspecified indicates that the server may assign a maximum." | VERIFIED |
| https://developers.google.com/workspace/classroom/reference/rest/v1/courses.students/list | not shown | "The default is 30 if unspecified or 0." | VERIFIED |
| https://stackoverflow.com/questions/70405402 | n/a (community) | "I get always 500 items when list Classroom" | NOT VERIFIED (community) |
| https://stackoverflow.com/questions/67395217 | n/a (community) | "chances are that's the maximum value too … doesn't seem to be documented" | NOT VERIFIED (community) |

### Verdict
**Q8:** No documented hard `pageSize` maximum for the three list methods (server "may assign a maximum" and may return fewer); `students.list` defaults to 30 (community suggests it's also the cap — unverified); community-observed ~500/page cap for `courses.list` (unverified). Implement `nextPageToken` loops unconditionally. **Confidence: high** for "no official max"; **low/medium** for the specific community-observed caps.

---

# What Lumio can build NOW vs. what is blocked

## Buildable now (static JS + GSI, zero server)
1. **Full read MVP:** GSI `initTokenClient` with `classroom.courses.readonly` + `classroom.coursework.me.readonly` → list own courses (incl. archived), each course's published work (title, description, dueDate/dueTime in UTC, maxPoints, materials, alternateLink), own submissions (state, late, **assignedGrade**, alternateLink). All data Lumio needs is in three list calls per course. (High confidence, Q1/Q3.)
2. **Own GCP project + consent screen + Web OAuth client** (free; `http://localhost:5173` allowed as JS origin; public HTTPS origin for production). Run in **Testing mode** with the student as a test user. (Q5/Q6.)
3. **Due-date display without grades/descriptions:** Google Takeout (manual, one-shot, JSON) for grades+submissions; Calendar ICS export (manual) for due dates — both user-initiated, no app needed, useful as an offline fallback or pre-consent preview. (Q7.)
4. **In-app polling** while the tab is open (well within 20 QPS/user/min). (Q4.)

## Blocked / requires more
1. **Background sync while PC is off / push:** impossible with GSI-only (no refresh token; consent in Testing mode expires in 7 days; no browser-side push). Options: (a) add a tiny backend for authorization-code flow + stored refresh token (unblocks offline token refresh and enables server-side Pub/Sub push with `classroom.push-notifications`); (b) rely on in-app polling only. Pub/Sub push additionally needs GCP Pub/Sub + billing and is unreliable for courses outside a WFE domain. (Q4.)
2. **Public distribution to other students:** requires Google OAuth app verification for sensitive Classroom scopes (security assessment, demo video, etc.) — multi-week process; until then 100-test-user cap + weekly test-mode re-consent + unverified-app screen. School WFE admins can additionally block the app per service. (Q2/Q5.)
3. **Reading other students / rosters / draft grades:** not possible by design with a student token. (Q3.)
4. **Full course metadata via Takeout (student side):** not documented for student exports; calendar lacks no-due-date items, grades, descriptions. (Q7.)

---

# Flat Sources list (all accessed 2026-11-11)

Official — developers.google.com:
1. https://developers.google.com/workspace/classroom/reference/rest/v1/courses/list — courses.list
2. https://developers.google.com/workspace/classroom/reference/rest/v1/courses — Course resource + CourseState (last updated 2026-11-02)
3. https://developers.google.com/workspace/classroom/reference/rest/v1/courses.courseWork — CourseWork resource (last updated 2026-11-02)
4. https://developers.google.com/workspace/classroom/reference/rest/v1/courses.courseWork/list — coursework.list
5. https://developers.google.com/workspace/classroom/reference/rest/v1/courses.courseWork.studentSubmissions — StudentSubmission resource
6. https://developers.google.com/workspace/classroom/reference/rest/v1/courses.courseWork.studentSubmissions/list — studentSubmissions.list (last updated 2026-06-10)
7. https://developers.google.com/workspace/classroom/reference/rest/v1/SubmissionState (last updated 2025-04-17)
8. https://developers.google.com/workspace/classroom/reference/rest/v1/courses.students/list — students.list (default pageSize 30)
9. https://developers.google.com/workspace/classroom/reference/limits — usage limits (last updated 2026-09-03)
10. https://developers.google.com/workspace/classroom/guides/auth — scopes table (last updated 2026-09-03)
11. https://developers.google.com/workspace/classroom/guides/push-notifications — Pub/Sub push notifications (last updated 2026-09-03)
12. https://developers.google.com/workspace/classroom/guides/classroom-api/manage-grades — draftGrade/assignedGrade (last updated 2026-09-03)
13. https://developers.google.com/workspace/classroom/guides/manage-coursework — role→scope mapping
14. https://developers.google.com/workspace/classroom/guides/onboarding/prerequisites — "no paid GCP features needed"
15. https://developers.google.com/workspace/classroom/add-ons/developer-guides/project-configuration — "Classroom scopes are Sensitive"
16. https://developers.google.com/workspace/classroom/guides/mcp/configure-mcp-server — official Classroom MCP server (own client required)
17. https://developers.google.com/identity/oauth2/web/reference/js-reference — GSI TokenResponse (no refresh_token)
18. https://developers.google.com/identity/oauth2/web/guides/use-token-model — token model (last updated 2026-05-26)
19. https://developers.google.com/identity/oauth2/web/guides/migration-to-gis — no auto-refresh in GSI; `expires_in: 3599`
20. https://developers.google.com/identity/protocols/oauth2/web-server — client creation, origins/redirect URIs, "must have authorization credentials"
21. https://developers.google.com/identity/protocols/oauth2 — "refresh token expiring in 7 days" for Testing projects
22. https://developers.google.com/identity/protocols/oauth2/production-readiness/overview — Testing/Trusted matrix, 100-user cap, 7-day expiry
23. https://developers.google.com/identity/protocols/oauth2/scopes — Google API scopes reference (Classroom section)
24. https://developers.google.com/resources/api-libraries/documentation/classroom/v1/python/latest/classroom_v1.courses.html — official client-lib (courseStates default list)

Official — support.google.com / knowledge.workspace.google.com:
25. https://support.google.com/cloud/answer/15549945 — Manage App Audience (100 test users; 7-day authorization expiry)
26. https://support.google.com/cloud/answer/15549257 — Manage OAuth Clients (JS origins / redirect URIs rules; localhost exempt)
27. https://support.google.com/cloud/answer/13463073 — OAuth App Verification Help Center (sensitive/restricted require verification)
28. https://support.google.com/cloud/answer/13464018 — Changes to approved app (100-user cap for unverified sensitive use)
29. https://support.google.com/cloud/answer/13461325 — Submitting your app for verification (External = starts in test mode)
30. https://support.google.com/edu/classroom/answer/10204459 — Export your data from Google Classroom (student datasets)
31. https://support.google.com/edu/classroom/answer/6272985 — View due dates and events in a calendar (students)
32. https://support.google.com/calendar/answer/37111 — Export events from your Google Calendar (ICS)
33. https://support.google.com/accounts/answer/3024190 — How to download your Google data (Takeout; scheduled = Photos only)
34. https://support.google.com/edu/classroom/answer/6023715 — Control user access to Classroom (admin)
35. https://knowledge.workspace.google.com/admin/apps/control-which-apps-access-google-workspace-data — admin app access control (last updated 2026-10-26)

Community / third-party (NOT VERIFIED as authority):
36. https://stackoverflow.com/questions/70405402 — "I get always 500 items when list Classroom"
37. https://stackoverflow.com/questions/67395217 — batch/paging; 30-cap observation
38. https://stackoverflow.com/questions/75725474 — bypassing unverified-app screen (community anecdote)
39. https://github.com/psvenk/classroom-export-viewer — Takeout Classroom = JSON; no announcements/materials
40. https://integrations.sadlierconnect.com/article/548 — third-party scope-sensitivity claim (contradicts official)

---

Cloud Console required for official Classroom API: YES — https://developers.google.com/workspace/classroom/guides/onboarding/prerequisites ("You must use a Google Cloud project to manage a Google Classroom integration. You don't need to use any paid Google Cloud features to use Classroom API.") + https://developers.google.com/identity/protocols/oauth2/web-server ("Any application that uses OAuth 2.0 to access Google APIs must have authorization credentials that identify the application to Google's OAuth 2.0 server.")
