import QtQuick 2.6
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Extras 1.4
import QtQuick.Layouts 1.3
import QtCharts 2.2
//import QtDataVisualization 1.3


Rectangle {
    id: dhmx_histogram
    objectName: "dhmx_histogram"
    visible: true
    width: 500
    height: 200
    //drag.target: dhmx_histogram
    color: "#00000000"

    /* This value will change depending on width/height totals of each camera.
     * e.g. 1024x1024 = 1048576 */
    property int bin_amnt: 65535

    /* Autoscale feature to be enabled or disabled by the user
     * If enabled, it will store a max value from each frame of 0 - 255 and use
     * that as its max */
    property bool autoscale: false
    property int max_val: 0
    property int permanent_max: 0


    ChartView{
        id: histogram_chart
        anchors.fill:parent
        legend.visible: false
        antialiasing: true
        backgroundColor: "transparent"
        ValueAxis{
            id: axisX
            labelsVisible: false
            gridVisible: false
        }
        ValueAxis{
            id: axisY
            labelsVisible: false
            gridVisible: false
        }

        BarSeries{
            id: series_histogram
            objectName: "series_histogram"
            axisX: axisX
            axisY: axisY
            barWidth: 0.1

            /* Values from 0 - 255 inclusive */
            BarSet{
                label: "histogram"
                id: barset_ammount
                objectName: "barset_ammount"
                values: [bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt, bin_amnt,
                         bin_amnt, bin_amnt, bin_amnt]
                onValueChanged: {
                   if(index == 255){
                       histogram_chart.update()
                   }
                }
            }
        }
    }

    function set_autoscaling(mode){
        /* Enabling autoscaling of the y-axis */
        if(mode == "enabled"){
            autoscale = true
        }

        /* This mode will disable autoscaling but keep the last y-value */
        else if (mode == "disabled"){
            autoscale = false
            axisY.max = permanent_max
        }

        /* This mode will completely reset the y-axis back to default which is width * height max y-value */
        else if (mode == "reset"){
            autoscale = false
            update_bins(bin_amnt)
        }
    }

    function update_bins(bins){
        bin_amnt = bins
        axisY.max = bin_amnt
    }

    function reset_chart(){
        histogram_chart.update()
    }

    function set_val(i,val){
        barset_ammount.replace(i,val)

        /* Set a max value if autoscaling is true */
        if(autoscale){
            if(val > max_val){
               max_val = val
            }
            if(i == 254){
                axisY.max = max_val
                permanent_max = max_val
                max_val = 0
            }
        }
    }

}
