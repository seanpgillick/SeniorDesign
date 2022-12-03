

//Need some code to get cities from DB and into Array
//Need some code to get year from selected city from DB into Array
//Need some code to get data from selected city and year from DB into array


// Will load cityArr data into the select option
var cityArr = ["...", "Denver", "Littleton", "Colorado Springs"]
var citySelect = document.getElementById("cities-select")
var yearSelect = document.getElementById("years-select")
var searchButton = document.getElementById("search-button")
searchButton.addEventListener("click", searchDB)
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

//Use this function to Query DB
function searchDB() {
    dataContainer = document.getElementById("db-data")
    while (dataContainer.firstChild) {
        dataContainer.removeChild(dataContainer.firstChild)
    }
    city = citySelect.value
    year = yearSelect.value
    let table = document.createElement('table')
    thOff = document.createElement('th')
    thLat = document.createElement('th')
    thLong = document.createElement('th')
    thOff.innerHTML = "Offense"
    thLat.innerHTML = "Latitude"
    thLong.innerHTML = "Longitude"
    headerRow = document.createElement('tr')
    headerRow.appendChild(thOff)
    headerRow.appendChild(thLat)
    headerRow.appendChild(thLong)
    table.appendChild(headerRow)
    table.style.border = '1px solid black'
    //THIS IS ALL TEMP
    let text = '{"response": [' + 
    '{ "offense":"Burglary" , "latitude":"42.33367921810846" , "longitude": "-71.09187754618458"},' +
    '{ "offense":"Murder" , "latitude":"42.33367921810846" , "longitude": "-71.09187754618458" },' +
    '{ "offense":"Theft" , "latitude":"42.33367921810846" , "longitude": "-71.09187754618458" } ]}';
    const response = JSON.parse(text)
    //END TEMP (TO BE REPLACED WITH DATABASE CODE)
    console.log(response.response)
    let num = -1
    for(entry of response.response) {
        var tr = table.insertRow();
        var td = tr.insertCell();
        td.appendChild(document.createTextNode(entry.offense))
        var tdLat = tr.insertCell();
        tdLat.appendChild(document.createTextNode(entry.latitude))
        var tdLong = tr.insertCell();
        tdLong.appendChild(document.createTextNode(entry.longitude))
        if(num == -1) {
            tr.style.backgroundColor="#D3D3D3"
        }
        num = num * -1
    }

    dataContainer.appendChild(table)


}