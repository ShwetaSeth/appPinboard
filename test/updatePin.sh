echo -e "\n"
curl -i -H "Content-Type: application/json" -X PUT -d '{"pinName":"Salad Love"}' http://192.168.0.7:5000/users/1/boards/Recipes/pins/1
echo -e "\n"

