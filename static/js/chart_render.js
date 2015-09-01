window.onload = function () {
    var playrate_chart = new CanvasJS.Chart("playrateChartContainer", {

        title: {
            text: "Playrate of Champions",
            fontColor: "#80acc4"
        },
        backgroundColor: "rgba(55, 98, 134, 0.90)",
        animationEnabled: true,
        axisX: {
            interval: 1,
            gridThickness: 0,
            labelFontSize: 10,
            labelFontStyle: "normal",
            labelFontWeight: "normal",
            labelFontColor: "#80acc4",
            labelFontFamily: "Lucida Sans Unicode"

        },
        axisY2: {
            labelFontColor: "#80acc4",
            interlacedColor: "rgba(1,77,101,.2)",
            gridColor: "rgba(1,77,101,.1)"

        },

        data: [
            {
                type: "bar",
                name: "Patch 5.11",
                showInLegend: true,
                axisYType: "secondary",
                color: "#A4A6D8",
                dataPoints: [
                    {label: "Teemo", y: 2.28},
                    {label: "Orianna", y: 1.82},
                    {label: "Ryze", y: 1.98},
                    {label: "Katarina", y: 3.05},
                    {label: "Diana", y: 3.04},
                    {label: "Nidalee", y: 3.27},
                    {label: "Fizz", y: 2.83},
                    {label: "Leblanc", y: 3.61},
                    {label: "Chogath", y: 3.48},
                    {label: "Lux", y: 3.8},
                    {label: "Ekko", y: 4.57},
                    {label: "Vladimir", y: 4.77},
                    {label: "Ahri", y: 4.55},
                    {label: "Annie", y: 6.04},
                    {label: "Morgana", y: 6.62}
                ]
            },
            {
                type: "bar",
                name: "Patch 5.14",
                showInLegend: true,
                axisYType: "secondary",
                color: "#7656A7",
                dataPoints: [
                    {label: "Teemo", y: 2.1},
                    {label: "Orianna", y: 2.21},
                    {label: "Ryze", y: 2.5},
                    {label: "Katarina", y: 2.98},
                    {label: "Diana", y: 3.04},
                    {label: "Nidalee", y: 3.16},
                    {label: "Fizz", y: 3.3},
                    {label: "Leblanc", y: 3.57},
                    {label: "Chogath", y: 3.71},
                    {label: "Lux", y: 3.81},
                    {label: "Ekko", y: 3.86},
                    {label: "Vladimir", y: 4.41},
                    {label: "Ahri", y: 5.13},
                    {label: "Annie", y: 6.08},
                    {label: "Morgana", y: 7.03}
                ]
            }


        ]
    });
    playrate_chart.render();
};