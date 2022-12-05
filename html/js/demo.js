//Need some code to get cities from DB and into Array
//Need some code to get year from selected city from DB into Array
//Need some code to get data from selected city and year from DB into array

// Will load cityArr data into the select option
var cityArr = ["...", "Denver", "Atlanta", "Austin", "Baltimore", "Boston", "Buffalo", "Chicago", "Cincinnati", "Colorado Springs", "Fort Worth", "Houston", "Kansas City", "Los Angeles", "Memphis", "Mesa", "Milwaukee", "Montgomery", "Nashville", "New York", "Omaha", "Philadelphia", "Portland", "Raleigh", "San Francisco", "Seattle", "Washington D.C."]
var citySelect = document.getElementById("cities-select")
var yearSelect = document.getElementById("years-select")
var searchButton = document.getElementById("search-button")
searchButton.disabled = true

for(element of cityArr)
{
   var opt = document.createElement("option");
   opt.value = element;
   opt.innerHTML = element; // whatever property it has

   // then append it to the select element
   citySelect.appendChild(opt);
}

//Called when city select option is changed
function validateCity(city) {
    //check if city is in DB, if so, call populate years with City

    if(city != "...") {
        populateYears(city)
    }
}

//Get available years from DB using city to query
function populateYears(city){
    //Get years from DB here

    //Put years into yearArr
    yearArr = ["...", "2019","2020","2021"]
    while (yearSelect.firstChild) {
        yearSelect.removeChild(yearSelect.firstChild)
    }
    for(element of yearArr)
        {
            var opt = document.createElement("option");
            opt.value = element;
            opt.innerHTML = element; // whatever property it has
            yearSelect.appendChild(opt);
        }
}

function validateYear(year) {
    //check if city is in DB, if so, call populate years with City
    let city = citySelect.value
    //this if will need to change to check if both the current selected city and year are valid
    if(year != "...") {
        searchButton.disabled = false
    }
}