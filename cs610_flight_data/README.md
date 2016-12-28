shiyanlou_cs610
===============

实验楼课程: [大数据带你看穿航班晚点的套路](https://www.shiyanlou.com/courses/610) 相关代码

## Data

```sh
wget http://labfile.oss.aliyuncs.com/courses/610/1998.csv.bz2
bunzip2 1998.csv.bz2

wget http://labfile.oss.aliyuncs.com/courses/610/airports.csv
```

## Command

### Load data

```scala
val flightData = sqlContext.read.format("com.databricks.spark.csv").option("header","true").load("/home/shiyanlou/Code/shiyanlou_cs610/1998.csv")
flightData.registerTempTable("flights")

val airportData = sqlContext.read.format("com.databricks.spark.csv").option("header","true").load("/home/shiyanlou/Code/shiyanlou_cs610/airports-csv.csv")
airportData.registerTempTable("airports")
```

### Query1

```scala
val queryFlightNumResult = sqlContext.sql("SELECT COUNT(FlightNum) FROM flights WHERE DepTime BETWEEN 0 AND 600")
queryFlightNumResult.take(1)

val queryFlightNumResult1 = sqlContext.sql("SELECT COUNT(FlightNum)/COUNT(DISTINCT DayofMonth) FROM flights WHERE Month = 1 AND DepTime BETWEEN 1001 AND 1400")
queryFlightNumResult1.take(1)
```

### Query2

```scala
val queryDestResult = sqlContext.sql("SELECT DISTINCT Dest, ArrDelay FROM flights WHERE ArrDelay = 0")
queryDestResult.head(5)

val queryDestResult2 = sqlContext.sql("SELECT DISTINCT Dest, COUNT(ArrDelay) AS delayTimes FROM flights where ArrDelay = 0 GROUP BY Dest ORDER BY delayTimes DESC")
queryDestResult2.head(10)

val queryDestResult3 = sqlContext.sql("SELECT DISTINCT state, SUM(delayTimes) AS s FROM (SELECT DISTINCT Dest, COUNT(ArrDelay) AS delayTimes FROM flights WHERE ArrDelay = 0 GROUP BY Dest ) a JOIN airports b ON a.Dest = b.iata GROUP BY state ORDER BY s DESC")
queryDestResult3.head(10)

queryDestResult3.save("/home/shiyanlou/QueryDestResult.csv", "com.databricks.spark.csv")
```

```sh
cd ~/QueryDestResult.csv/
cat part-* >> result.csv
cp result.csv /home/shiyanlou/Code/shiyanlou_cs610/
```

### Query3

```scala
val queryOriginResult = sqlContext.sql("SELECT DISTINCT Origin, DepDelay FROM flights where DepDelay > 60 ORDER BY DepDelay DESC")
queryOriginResult.head(10)
```