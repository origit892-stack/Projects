mkdir -p assets/generated_meshes
while read item; do
    echo "Starting: $item"
    python3 ~/nexus_custom_tools/cube3d_generator.py -p "$item"
    safe_name=$(echo "$item" | tr ' ' '_').obj
    mv ~/cube/outputs/"$safe_name" assets/generated_meshes/ 2>/dev/null
done < asset_list.txt
