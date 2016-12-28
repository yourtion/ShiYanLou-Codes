import org.apache.spark._
import org.apache.spark.rdd.RDD
import org.apache.spark.mllib.util.MLUtils
import org.apache.spark.mllib.linalg.Vectors
import org.apache.spark.mllib.regression.LabeledPoint
import org.apache.spark.mllib.tree.DecisionTree
import org.apache.spark.mllib.tree.model.DecisionTreeModel

val tmpFlightDataRDD = flightData.map(row => row(2).toString+","+row(3).toString+","+row(5).toString+","+row(7).toString+","+row(8).toString+","+row(12).toString+","+ row(16).toString+","+row(17).toString+","+row(14).toString+","+row(15).toString)

case class Flight(dayOfMonth:Int, dayOfWeek:Int, crsDepTime:Double, crsArrTime:Double, uniqueCarrier:String, crsElapsedTime:Double, origin:String, dest:String, arrDelay:Int, depDelay:Int, delayFlag:Int)

def parseFields(input: String): Flight = {
  val line = input.split(",")

  var dayOfMonth = 0
  if(line(0) != "NA"){
    dayOfMonth = line(0).toInt
  }
  var dayOfWeek = 0
  if(line(1) != "NA"){
    dayOfWeek = line(1).toInt
  }

  var crsDepTime = 0.0
  if(line(2) != "NA"){
    crsDepTime = line(2).toDouble
  }

  var crsArrTime = 0.0
  if(line(3) != "NA"){
    crsArrTime = line(3).toDouble
  }

  var crsElapsedTime = 0.0
  if(line(5) != "NA"){
    crsElapsedTime = line(5).toDouble
  }

  var arrDelay = 0
  if(line(8) != "NA"){
    arrDelay = line(8).toInt
  }
  var depDelay = 0
  if(line(9) != "NA"){
    depDelay = line(9).toInt
  }

  var delayFlag = 0
  if(arrDelay > 30 || depDelay > 30){
    delayFlag = 1
  }
  Flight(dayOfMonth, dayOfWeek, crsDepTime, crsArrTime, line(4), crsElapsedTime, line(6), line(7), arrDelay, depDelay, delayFlag)
}

val flightRDD = tmpFlightDataRDD.map(parseFields)
flightRDD.take(1)

var id: Int = 0
var mCarrier: Map[String, Int] = Map()
flightRDD.map(flight => flight.uniqueCarrier).distinct.collect.foreach(x => {mCarrier += (x -> id); id += 1})
mCarrier.toString

var id_1: Int = 0
var mOrigin: Map[String, Int] = Map()
flightRDD.map(flight => flight.origin).distinct.collect.foreach(x => {mOrigin += (x -> id_1); id_1 += 1})

var id_2: Int = 0
var mDest: Map[String, Int] = Map()
flightRDD.map(flight => flight.dest).distinct.collect.foreach(x => {mDest += (x -> id_2); id_2 += 1})

val featuredRDD = flightRDD.map(flight => {
  val vDayOfMonth = flight.dayOfMonth - 1
  val vDayOfWeek = flight.dayOfWeek - 1
  val vCRSDepTime = flight.crsDepTime
  val vCRSArrTime = flight.crsArrTime
  val vCarrierID = mCarrier(flight.uniqueCarrier)
  val vCRSElapsedTime = flight.crsElapsedTime
  val vOriginID = mOrigin(flight.origin)
  val vDestID = mDest(flight.dest)
  val vDelayFlag = flight.delayFlag

  Array(vDelayFlag.toDouble, vDayOfMonth.toDouble, vDayOfWeek.toDouble, vCRSDepTime.toDouble, vCRSArrTime.toDouble, vCarrierID.toDouble, vCRSElapsedTime.toDouble, vOriginID.toDouble, vDestID.toDouble)
})
featuredRDD.take(1)


val LabeledRDD = featuredRDD.map(x => LabeledPoint(x(0), Vectors.dense(x(1), x(2), x(3), x(4), x(5), x(6), x(7), x(8))))
LabeledRDD.take(1)

val notDelayedFlights = LabeledRDD.filter(x => x.label == 0).randomSplit(Array(0.8, 0.2))(1)
val delayedFlights = LabeledRDD.filter(x => x.label == 1)
val tmpTTData = notDelayedFlights ++ delayedFlights
val TTData = tmpTTData.randomSplit(Array(0.7, 0.3))
val trainingData = TTData(0)
val testData = TTData(1)

var paramCateFeaturesInfo = Map[Int, Int]()
paramCateFeaturesInfo += (0 -> 31)
paramCateFeaturesInfo += (1 -> 7)
paramCateFeaturesInfo += (4 -> mCarrier.size)
paramCateFeaturesInfo += (6 -> mOrigin.size)
paramCateFeaturesInfo += (7 -> mDest.size)
val paramNumClasses = 2
val paramMaxDepth = 9
val paramMaxBins = 7000
val paramImpurity = "gini"

val flightDelayModel = DecisionTree.trainClassifier(trainingData, paramNumClasses, paramCateFeaturesInfo, paramImpurity, paramMaxDepth, paramMaxBins)
val tmpDM = flightDelayModel.toDebugString
print(tmpDM)

val predictResult = testData.map{flight => 
  val tmpPredictResult = flightDelayModel.predict(flight.features)
  (flight.label, tmpPredictResult)
}
predictResult.take(10)

val numOfCorrectPrediction = predictResult.filter{case (label, result) => (label == result)}.count()

val predictAccuracy = numOfCorrectPrediction/testData.count().toDouble
