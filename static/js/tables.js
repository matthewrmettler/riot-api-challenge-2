//color rows
var colorRows = function () {
    colorGradient = [rgba(119, 136, 102, 0.85), rgba(125, 115, 0.85), rgb(132, 95, 81), rgb(139, 74, 71), rgb(146, 54, 61), rgb(153, 34, 51)];
    console.log("color rows");
    $("#winrate-table").find("tr").each(function () {
        var win_percent = $(this).find('td').eq(6).text();
        console.log(win_percent);
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
};



//winrate table
$.getJSON( "https://api.myjson.com/bins/2zev2", function( data ) {
    console.log(data);
    //winrates = JSON.parse(data);
    $('#winrate-table').dynatable({
        dataset: {
            records: data,
            perPageDefault: 100
        },
        features: {
            paginate: false,
            recordCount: false
        }
    }).bind('dynatable:afterProcess', colorRows);
});

colorRows();