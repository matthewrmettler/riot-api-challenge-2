//color rows
var colorRows = function () {
    var colorGradient = ["rgb(119, 136, 102)", "rgb(125, 115, 91)", "rgb(132, 95, 81)", "rgb(139, 74, 71)", "rgb(146, 54, 61)", "rgb(153, 34, 51)"];
    console.log("color rows");

    $("#winrate-table").find("tr").each(function () {
        var win_percent = $(this).find('td').eq(6).text();
        if (parseFloat(win_percent) >= 55.0) {
            $(this).css("background-color", colorGradient[0])
        } else if (parseFloat(win_percent) >= 52.5) {
            $(this).css("background-color", colorGradient[1])
        } else if (parseFloat(win_percent) >= 50.0) {
            $(this).css("background-color", colorGradient[2])
        } else if (parseFloat(win_percent) >= 47.5) {
            $(this).css("background-color", colorGradient[3])
        } else if (parseFloat(win_percent) >= 45.0) {
            $(this).css("background-color", colorGradient[4])
        } else {
            $(this).css("background-color", colorGradient[5])
        }
    });

    $("#rylais-table").find("tr").each(function () {
        var win_percent = $(this).find('td').eq(8).text();
        if (parseFloat(win_percent) >= 55.0) {
            $(this).css("background-color", colorGradient[0])
        } else if (parseFloat(win_percent) >= 52.5) {
            $(this).css("background-color",  colorGradient[1])
        } else if (parseFloat(win_percent) >= 50.0) {
            $(this).css("background-color",  colorGradient[2])
        } else if (parseFloat(win_percent) >= 47.5) {
            $(this).css("background-color",  colorGradient[3])
        } else if (parseFloat(win_percent) >= 45.0) {
            $(this).css("background-color",  colorGradient[4])
        } else {
            $(this).css("background-color",  colorGradient[5])
        }
    });

    $("#damage-table").find("tr").each(function () {
        var kda = $(this).find('td').eq(11).text();
        if (parseFloat(kda) >= 25.0) {
            $(this).css("background-color", colorGradient[0])
        } else if (parseFloat(kda) >= 20.0) {
            $(this).css("background-color",  colorGradient[1])
        } else if (parseFloat(kda) >= 15.0) {
            $(this).css("background-color",  colorGradient[2])
        } else if (parseFloat(kda) >= 10.0) {
            $(this).css("background-color",  colorGradient[3])
        } else if (parseFloat(kda) >= 5.0) {
            $(this).css("background-color",  colorGradient[4])
        } else {
            $(this).css("background-color",  colorGradient[5])
        }
    });
};

//add icons to champ name
var portraits = function() {
    $("#winrate-table").find("tr").each(function () {
        var championCell = $(this).find('td').eq(0);
        if (!championCell.find('img').length) {
            var championName = championCell.text();
            var portrait = "<img class='portrait' src='http://ddragon.leagueoflegends.com/cdn/5.14.1/img/champion/" + championName + ".png' />";
            $(championCell).prepend(portrait);
        }
    });

    $("#rylais-table").find("tr").each(function () {
        var championCell = $(this).find('td').eq(0);
        if (!championCell.find('img').length)  {
            var championName = championCell.text();
            var portrait = "<img class='portrait' src='http://ddragon.leagueoflegends.com/cdn/5.14.1/img/champion/" + championName + ".png' />";
            $(championCell).prepend(portrait);
        }
    });

    $("#damage-table").find("tr").each(function () {
        var championCell = $(this).find('td').eq(0);
        if (!championCell.find('img').length) {
            var championName = championCell.text();
            var portrait = "<img class='portrait' src='http://ddragon.leagueoflegends.com/cdn/5.14.1/img/champion/" + championName + ".png' />";
            $(championCell).prepend(portrait);
        }
    });
};

var updateWinrate = function() {
    portraits();
    colorRows();
};

//winrate table
//If this stops working, use the json file at static/json/winrate.json
$.getJSON( "https://api.myjson.com/bins/2zev2", function( data ) {
    $('#winrate-table').dynatable({
        dataset: {
            records: data,
            perPageDefault: 100
        },
        features: {
            paginate: false,
            recordCount: false
        }
    }).bind('dynatable:afterProcess', updateWinrate);
});

//rylais table
//If this stops working, use the json file at static/json/rylais.json
$.getJSON("https://api.myjson.com/bins/59rda", function( data ) {
    $('#rylais-table').dynatable({
        dataset: {
            records: data,
            perPageDefault: 100
        },
        features: {
            paginate: false,
            recordCount: false
        }
    }).bind('dynatable:afterProcess', updateWinrate);
});

//damage table
//If this stops working, use the json file at static/json/damage.json
$.getJSON("https://api.myjson.com/bins/3np3a", function( data ) {
    $('#damage-table').dynatable({
        dataset: {
            records: data,
            perPageDefault: 100
        },
        features: {
            paginate: false,
            recordCount: false
        }
    }).bind('dynatable:afterProcess', updateWinrate);
});

$(window).load( function() {
    updateWinrate();
});

updateWinrate();