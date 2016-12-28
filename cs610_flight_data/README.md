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
