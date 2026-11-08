#!/bin/bash
echo ""
echo "==================================================="
echo " 🔍 NEXUS READ-ONLY SYSTEM HEALTH CHECK"
echo "==================================================="
echo ""

PROJECT_DIR=~/Documents/Projects/BunkerGame
CUBE_DIR=~/cube
TOOL_PATH=~/nexus_custom_tools/cube3d_generator.py

echo "📁 1. Checking Directories..."
[ -d "$PROJECT_DIR" ] && echo "  [OK] Project directory found." || echo "  [ERROR] Project directory missing!"
[ -d "$PROJECT_DIR/assets/generated_meshes" ] && echo "  [OK] Target meshes directory exists." || echo "  [WARNING] Target meshes directory missing."
[ -d "$CUBE_DIR/outputs" ] && echo "  [OK] Cube engine outputs directory found." || echo "  [ERROR] Cube engine outputs directory missing!"

echo ""
echo "📄 2. Checking Critical Files..."
[ -f "$PROJECT_DIR/asset_list.txt" ] && echo "  [OK] asset_list.txt found." || echo "  [ERROR] asset_list.txt missing!"
[ -f "$TOOL_PATH" ] && echo "  [OK] cube3d_generator.py tool found." || echo "  [ERROR] cube3d_generator.py missing!"
[ -f "$PROJECT_DIR/builder_bot.py" ] && echo "  [OK] builder_bot.py script found." || echo "  [ERROR] builder_bot.py missing!"

echo ""
echo "🐍 3. Checking Python Environment..."
[ -d "$CUBE_DIR/venv" ] && echo "  [OK] Python Virtual Environment (venv) found." || echo "  [ERROR] Python venv missing in $CUBE_DIR!"

echo ""
echo "💾 4. Checking System Resources..."
FREE_SPACE=$(df -h / | awk 'NR==2 {print $4}')
echo "  [INFO] Free Disk Space on main drive: $FREE_SPACE"

echo ""
echo "==================================================="
echo " 🏁 HEALTH CHECK COMPLETE"
echo "==================================================="
echo ""
