//Connects to database
var mysql = require('mysql');

var con = mysql.createConnection({
    host: "seniordesign-db.cxwhjsfccgui.us-east-1.rds.amazonaws.com",
    user: "admin",
    password: "password!"
});
  

//Gets all the cities in the table
var queryCity = 'SELECT City FROM SeniorDesign.CrimeData GROUP BY City';

//Gets all the years in the table
var queryYear = 'SELECT Year(Date) FROM SeniorDesign.CrimeData GROUP BY Year(Date)';

//Gets the results from your selection
//var querySelected = 'SELECT * FROM SeniorDesign.CrimeData WHERE City="' + city + '" AND Year(Date)="' + year + '"';


//Connect to the database and perform queries
con.connect(function(err) {
    if (err) throw err;
    console.log("Connected!");
    con.query(queryCity, function (err, result, fields) {
        if (err) throw err;
        console.log(result);
    });
    con.query(queryYear, function (err, result, fields) {
        if (err) throw err;
        console.log(result);
    });
});
