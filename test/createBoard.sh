echo -e "\n" 
curl -i -H "Content-Type: application/json" -X POST -d '{"boardName":"Recipes","boardDesc":"Indian food recipes","category":"Food","isPrivate":"false"}' http://192.168.0.7:5000/users/1/boards
echo -e "\n"


