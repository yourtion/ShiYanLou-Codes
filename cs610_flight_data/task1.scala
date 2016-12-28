import org.apache.spark._
import org.apache.spark.rdd.RDD
import org.apache.spark.mllib.util.MLUtils
import org.apache.spark.mllib.linalg.Vectors
import org.apache.spark.mllib.regression.LabeledPoint
import org.apache.spark.mllib.tree.DecisionTree
import org.apache.spark.mllib.tree.model.DecisionTreeModel

val flightData = sqlContext.read.format("com.databricks.spark.csv").option("header","true").load("/home/shiyanlou/Code/shiyanlou_cs610/1998.csv")
flightData.registerTempTable("flights")

val airportData = sqlContext.read.format("com.databricks.spark.csv").option("header","true").load("/home/shiyanlou/Code/shiyanlou_cs610/airports-csv.csv")
airportData.registerTempTable("airports")

// #DataFrame 转换为 RDD

// 从 DataFrame 类型转换为 RDD 类型。从 row 中取值时是按照数据集中各个字段取出 Flight 类中对应字段的值。
val tmpFlightDataRDD = flightData.map(row => row(2).toString+","+row(3).toString+","+row(5).toString+","+row(7).toString+","+row(8).toString+","+row(12).toString+","+ row(16).toString+","+row(17).toString+","+row(14).toString+","+row(15).toString)

// 建立一个类，将 RDD 中的部分字段映射到类的成员变量中。
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

  // 标签有两种，如果 delayFlag 为 1 ，则代表航班有延误；如果为 0 ，则代表没有延误。
  var delayFlag = 0
  if(arrDelay > 30 || depDelay > 30){
    delayFlag = 1
  }
  Flight(dayOfMonth, dayOfWeek, crsDepTime, crsArrTime, line(4), crsElapsedTime, line(6), line(7), arrDelay, depDelay, delayFlag)
}

val flightRDD = tmpFlightDataRDD.map(parseFields)
// 取出一个值检查解析是否成功。
flightRDD.take(1)

// # 提取特征
// 字符串类型的特征转换为含有唯一 ID 的数值特征（如 “AA” 变成了 0，“AS” 变成了1，以此类推，实际运算时是按照字母先后顺序进行标记的）。

// 航空公司代码的字符串到对应的唯一 ID 之间的转换
var id: Int = 0
var mCarrier: Map[String, Int] = Map()
flightRDD.map(flight => flight.uniqueCarrier).distinct.collect.foreach(x => {mCarrier += (x -> id); id += 1})
mCarrier.toString

// 出发地 Origin 的字符串到对应的唯一 ID 之间的转换
var id_1: Int = 0
var mOrigin: Map[String, Int] = Map()
flightRDD.map(flight => flight.origin).distinct.collect.foreach(x => {mOrigin += (x -> id_1); id_1 += 1})

// 目的地 Dest 的字符串到对应的唯一 ID 之间的转换
var id_2: Int = 0
var mDest: Map[String, Int] = Map()
flightRDD.map(flight => flight.dest).distinct.collect.foreach(x => {mDest += (x -> id_2); id_2 += 1})

// # 定义特征数组

// 用不同的数字代表了不同的特征，这些特征最后都将放入数组中，可以将其理解为建立了特征向量。
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

  // 返回值中，将所有字段都转换成Double类型以利于建模时使用相关API
  Array(vDelayFlag.toDouble, vDayOfMonth.toDouble, vDayOfWeek.toDouble, vCRSDepTime.toDouble, vCRSArrTime.toDouble, vCarrierID.toDouble, vCRSElapsedTime.toDouble, vOriginID.toDouble, vDestID.toDouble)
})
featuredRDD.take(1)

// # 创建标记点
// 将含有特征数组的 featuredRDD 转换为含有 org.apache.spark.mllib.regression.LabeledPoint 包中定义的标记点 LabeledPoints 的新 RDD 。在分类中，标记点含有两类信息，一是代表了数据点的标记，二是代表了特征向量类。

val LabeledRDD = featuredRDD.map(x => LabeledPoint(x(0), Vectors.dense(x(1), x(2), x(3), x(4), x(5), x(6), x(7), x(8))))
LabeledRDD.take(1)

// 使用随机划分的方法，划分为训练集和测试集
// 未延迟航班总数的 80% ，将与所有的已延迟航班组成新的数据集。新数据集的 70% 和 30% 将被划分为训练集和测试集。

// 末尾的(1)是为了取这 80% 的部分
val notDelayedFlights = LabeledRDD.filter(x => x.label == 0).randomSplit(Array(0.8, 0.2))(1)
// 提取所有的已延迟航班。
val delayedFlights = LabeledRDD.filter(x => x.label == 1)
// 将上述二者组合成新的数据集
val tmpTTData = notDelayedFlights ++ delayedFlights
// 按照约定的比例随机划分为训练集和测试集
val TTData = tmpTTData.randomSplit(Array(0.7, 0.3))
val trainingData = TTData(0)
val testData = TTData(1)

// # 训练模型
// Spark MLlib中的决策树 (决策树类 DecisionTree 自带的 trainClassifier 方法)

// 仿照 API 文档中的提示，构造各项参数
var paramCateFeaturesInfo = Map[Int, Int]()
// 第一个特征信息：下标为 0 ，表示 dayOfMonth 有 0 到 30 的取值。
paramCateFeaturesInfo += (0 -> 31)
// 第二个特征信息：下标为 1 ，表示 dayOfWeek 有 0 到 6 的取值。
paramCateFeaturesInfo += (1 -> 7)
// 第三、四个特征是出发和抵达时间，这里我们不会用到，故省略。
// 第五个特征信息：下标为 4 ，表示 uniqueCarrier 的所有取值。
paramCateFeaturesInfo += (4 -> mCarrier.size)
// 第六个特征信息为飞行时间，同样忽略。
// 第七个特征信息：下标为 6 ，表示 origin 的所有取值。
paramCateFeaturesInfo += (6 -> mOrigin.size)
// 第八个特征信息：下标为 7， 表示 dest 的所有取值。
paramCateFeaturesInfo += (7 -> mDest.size)
// 分类的数量为 2，代表已延误航班和未延误航班。
val paramNumClasses = 2
// 下面的参数设置为经验值
val paramMaxDepth = 9
val paramMaxBins = 7000
val paramImpurity = "gini"

val flightDelayModel = DecisionTree.trainClassifier(trainingData, paramNumClasses, paramCateFeaturesInfo, paramImpurity, paramMaxDepth, paramMaxBins)
val tmpDM = flightDelayModel.toDebugString
// 打印出这棵决策树
print(tmpDM)

// # 测试模型

// // 使用决策树模型的predict方法按照输入进行预测，预测结果临时存放于 tmpPredictResult 中。最后与输入信息的标记组成元祖，作为最终的返回结果。
val predictResult = testData.map{flight => 
  val tmpPredictResult = flightDelayModel.predict(flight.features)
  (flight.label, tmpPredictResult)
}
predictResult.take(10)

// 按照这个评价标准来统计有多少条预测记录是准确的。
val numOfCorrectPrediction = predictResult.filter{case (label, result) => (label == result)}.count()

// 计算预测的正确率
val predictAccuracy = numOfCorrectPrediction/testData.count().toDouble
