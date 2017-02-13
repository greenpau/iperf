# iperf3-elastic

iPerf JSON client report parser for Elasticsearch.

For each input report, there are two (2) types of output records:

* Summary - a single record
* Intervals - multiple records based on the number of intervals
  in a report

Run the following command to create `elasticsearch` input:

```
iperf3-elastic.py --input iperf3-elastic.report.json
```
