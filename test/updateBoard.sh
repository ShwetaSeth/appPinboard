echo -e "\n"
curl -i -H "Content-Type: application/json" -X PUT -d '{"boardName":"Recipes","category":"categtory_changed", "boardDesc":"description_changed"}' http://192.168.0.7:5000/users/1/boards/Recipes
echo -e "\n"

