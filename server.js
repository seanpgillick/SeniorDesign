const express = require("express");
const app = express();
const mysql = require("mysql");


app.use(express.json())
app.use(express.static("html"));

// Post request - Calls the DB and returns all the results for a city within the given Year
app.post('/getData', function (req, res) {
    var city = req.body.City;
    var year = req.body.Year;

	// Config your database credential
	var con = mysql.createConnection({
        host: "seniordesign-db.cxwhjsfccgui.us-east-1.rds.amazonaws.com",
        port: "3306",
        user: "admin",
        password: "password!"
      });

    var minDate = year+"0101";
    var maxDate;

    if(year == 2019){
        maxDate = "20200101";
    } else {
        maxDate = (parseInt(year)+1)+"0101";
    }

    var query = 'SELECT * FROM SeniorDesign.CrimeData WHERE City="' + city + '" AND Date >= ' + minDate + ' AND Date < ' + maxDate + ';'

    con.connect(function(err) {
        if (err) throw err;
        console.log("Connected!");
        con.query(query, function (err, result) {
            if (err) throw err;
            res.send(result);
            con.end();
        });
    });

});

var server = app.listen(5000, function () {
	console.log('Server is listening at port 5000...');
});
