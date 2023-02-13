const express = require("express");
const app = express();
const mysql = require("mysql");
const { PORT = 3000} = process.env

console.log("PORT: ", PORT)

app.use(express.json());
app.use(express.static(__dirname + "/public"));
//setting view engine to ejs
app.set("view engine", "ejs");

var con = mysql.createConnection({
  host: "seniordesign-db.cxwhjsfccgui.us-east-1.rds.amazonaws.com",
  port: "3306",
  user: "admin",
  password: "password!",
});

//route for index page
app.get("/", function (req, res) {
  con.query(
    "SELECT City FROM SeniorDesign.CrimeData GROUP BY City",
    function (err, cities) {
      if (err) {
        req.flash("error", err);
        res.render("index", { cities: "", years: "" });
      } else {
        con.query(
          "SELECT Year(Date) AS Year FROM SeniorDesign.CrimeData GROUP BY Year(Date)",
          function (err, years) {
            if (err) {
              req.flash("error", err);
              res.render("index", { cities: "", years: "" });
            } else {
              res.render("index", { cities: cities, years: years });
            }
          }
        );
      }
    }
  );
});


// Post request - Calls the DB and returns all the results for a city within the given Year
app.post("/getData", function (req, res) {
  var city = req.body.City;
  var year = req.body.Year;

  // Config your database credential

  var minDate = year + "0101";
  var maxDate;

  if (year == 2019) {
    maxDate = "20200101";
  } else {
    maxDate = parseInt(year) + 1 + "0101";
  }

  var query =
    'SELECT * FROM SeniorDesign.CrimeData WHERE City="' +
    city +
    '" AND Date >= ' +
    minDate +
    " AND Date < " +
    maxDate +
    ";";

  con.query(query, function (err, result) {
    if (err) throw err;
    res.send(result);
  });
});


// var server = app.listen(5000, function () {
//   console.log("Server is listening at port 5000...");
// });

app.listen(PORT, () =>
  console.log(`App listening at http://localhost:${PORT}`)
)
