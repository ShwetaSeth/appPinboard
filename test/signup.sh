echo -e "\n"
curl -i -H "Content-Type: application/json" -X POST -d '{"firstName":"Bharat","lastName":"Mehndiratta","emailId":"bharat@gmail.com","password":"bharat16"}' http://192.168.0.7:5000/users/signup
echo -e "\n"
