import matplotlib.pyplot as plt

file = open('benchmark_results.txt', 'r')
lines = file.readlines()
n_lines = len(lines)
n_tests = int(n_lines/5)

datasets =[]
spark_times=[]
hadoop_times=[]
instances = 0
#Loop through all wordcount results 
for i in range(n_tests):
    #format the data that will be used to create graphs
    key = lines[i*5].replace("\n","")
    spark_minutes = lines[i*5+2].replace("\n","").split("m")
    spark_minutes[1]=spark_minutes[1].replace("s","")
    spark_seconds = float(spark_minutes[0])*60+float(spark_minutes[1])

    hadoop_minutes = lines[i*5+4].replace("\n","").split("m")
    hadoop_minutes[1]=hadoop_minutes[1].replace("s","")
    hadoop_seconds = float(hadoop_minutes[0])*60+float(hadoop_minutes[1])
    if key in datasets:
        instances += 1
        spark_times[i%9]+=spark_seconds
        hadoop_times[i%9]+=hadoop_seconds
    else:
        datasets.append(key)
        spark_times.append(spark_seconds)
        hadoop_times.append(hadoop_seconds)
      
file.close()
instances = 1 + instances/9 #obtain the amaount of times the datasets were processed by spark and hadoop

#Obtain average times
spark_res = []
for val in spark_times:
    spark_res.append(val/instances)
hadoop_res = []
for val in hadoop_times:
    hadoop_res.append(val/instances)
#Create performance graph
plt.plot(datasets,spark_res,hadoop_res)
plt.title('Performance Comparison of Hadoop and Spark')
plt.ylabel('Real Seconds Average')
plt.xlabel('Datasets')
plt.xticks(rotation=90)
plt.legend(['Spark times','Hadoop times'])
#Output graph to an image file
plt.savefig('HadoopVsSpark.png')
