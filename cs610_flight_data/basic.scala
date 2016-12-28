val flightData = sqlContext.read.format("com.databricks.spark.csv").option("header","true").load("/home/shiyanlou/Code/shiyanlou_cs610/1998.csv")
flightData.registerTempTable("flights")

val airportData = sqlContext.read.format("com.databricks.spark.csv").option("header","true").load("/home/shiyanlou/Code/shiyanlou_cs610/airports-csv.csv")
airportData.registerTempTable("airports")

// Query1 每天航班最繁忙的时间段是哪些

// 统计离港时间在 0 点 至 6 点 间的航班总数
val queryFlightNumResult = sqlContext.sql("SELECT COUNT(FlightNum) FROM flights WHERE DepTime BETWEEN 0 AND 600")
queryFlightNumResult.take(1)

// 统计离港时间只选择 1 个月的数据，时间段为 10:00 至 14:00 
val queryFlightNumResult1 = sqlContext.sql("SELECT COUNT(FlightNum)/COUNT(DISTINCT DayofMonth) FROM flights WHERE Month = 1 AND DepTime BETWEEN 1001 AND 1400")
queryFlightNumResult1.take(1)

// Query2 飞哪最准时

// 港延误时间为 0 的航班都是飞往哪里的。
val queryDestResult = sqlContext.sql("SELECT DISTINCT Dest, ArrDelay FROM flights WHERE ArrDelay = 0")
queryDestResult.head(5)

// 到港航班延误时间为 0 的次数（准点次数），并且最终输出的结果为 [目的地， 准点次数]
val queryDestResult2 = sqlContext.sql("SELECT DISTINCT Dest, COUNT(ArrDelay) AS delayTimes FROM flights where ArrDelay = 0 GROUP BY Dest ORDER BY delayTimes DESC")
queryDestResult2.head(10)

// 通过一个联结操作将 airports 表中每个机场都给出了它所在的州的信息（state）
val queryDestResult3 = sqlContext.sql("SELECT DISTINCT state, SUM(delayTimes) AS s FROM (SELECT DISTINCT Dest, COUNT(ArrDelay) AS delayTimes FROM flights WHERE ArrDelay = 0 GROUP BY Dest ) a JOIN airports b ON a.Dest = b.iata GROUP BY state ORDER BY s DESC")
queryDestResult3.head(10)

// 输出为 CSV 格式
queryDestResult3.save("/home/shiyanlou/QueryDestResult.csv", "com.databricks.spark.csv")

// Query3 出发延误的重灾区都有哪些

// 设置查询条件为离港延误时间大于 60 分钟
val queryOriginResult = sqlContext.sql("SELECT DISTINCT Origin, DepDelay FROM flights where DepDelay > 60 ORDER BY DepDelay DESC")
queryOriginResult.head(10)
