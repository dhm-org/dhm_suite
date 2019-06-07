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

            BarSet{
                label: "test"
                id: barset_ammount
                objectName: "barset_ammount"
                values: [65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535, 65535, 65535, 65535, 65535,
                         65535, 65535, 65535]
                onValueChanged: {
                   if(index == 255){
                       histogram_chart.update()
                   }
                }
            }
        }
    }


    function set_val(i,val){
        barset_ammount.replace(i,val)
    }

}
