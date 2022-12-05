//This Script Calls the DataBase and returns all entries for a given City within the specified range.
//The City and Year values are pulled from the dropdowns in index.html 

document.getElementById("search-button").addEventListener("click", function () {
    var city = document.getElementById("cities-select").value;
    var year = document.getElementById("years-select").value;
    dataContainer = document.getElementById("db-data")
    while (dataContainer.firstChild) {
        dataContainer.removeChild(dataContainer.firstChild)
    }

    //Call server.js to query the DB
	fetch("/getData", {
		method: "POST",
		headers: {
			"Content-Type": "application/json"
		},
		body: JSON.stringify({
			City: city,
            Year: year
		})
	})
    .then(response => response.json())
    .then(data => {
        //If there are any results, begin entering them into the table.
        if (data.length > 0){
            PopulatePage(data);
        }
        //If there are no results, indicate that the data is not available.
        else {
            const node = document.createTextNode("Crime Data not available.");
            dataContainer.appendChild(node);
        }
    });
});


//Populates the table on index.html.
function PopulatePage(results){
    console.log("Loading Data")
    dataContainer = document.getElementById("db-data")
    while (dataContainer.firstChild) {
        dataContainer.removeChild(dataContainer.firstChild)
    }
    var city = document.getElementById("cities-select").value;
    var year = document.getElementById("years-select").value;
    let table = document.createElement('table')

    //Table Headers
    thCity = document.createElement('th')
    thDate = document.createElement('th')
    thOff = document.createElement('th')
    thLat = document.createElement('th')
    thLong = document.createElement('th')
    thCity.innerHTML = "City"
    thDate.innerHTML = "Date"
    thOff.innerHTML = "Offense"
    thLat.innerHTML = "Latitude"
    thLong.innerHTML = "Longitude"

    //Table Rows
    headerRow = document.createElement('tr')
    headerRow.appendChild(thCity)
    headerRow.appendChild(thDate)
    headerRow.appendChild(thOff)
    headerRow.appendChild(thLat)
    headerRow.appendChild(thLong)
    table.appendChild(headerRow)
    table.style.border = '1px solid black'

    let num = -1
    //Loop through each entry returned. Create a cell for the City, Date, Offense, Latitude, and Longitude
    for(entry of results) {
        var tr = table.insertRow();
        var tdCity = tr.insertCell();
        tdCity.appendChild(document.createTextNode(entry.City))
        var tdDate = tr.insertCell();
        tdDate.appendChild(document.createTextNode(entry.Date))
        var tdOff = tr.insertCell();
        tdOff.appendChild(document.createTextNode(entry.Offense))  
        var tdLat = tr.insertCell();
        tdLat.appendChild(document.createTextNode(entry.Latitude))
        var tdLong = tr.insertCell();
        tdLong.appendChild(document.createTextNode(entry.Longitude))
        if(num == -1) {
            tr.style.backgroundColor="#D3D3D3"
        }
        num = num * -1
    }

    //Append the new Table into index.html
    dataContainer.appendChild(table)

    console.log("Finished Loading")
}
