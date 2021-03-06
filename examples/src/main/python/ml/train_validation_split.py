#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from pyspark import SparkContext
# $example on$
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.regression import LinearRegression
from pyspark.ml.tuning import ParamGridBuilder, TrainValidationSplit
from pyspark.sql import SQLContext
# $example off$

"""
This example demonstrates applying TrainValidationSplit to split data
and preform model selection.
Run with:

  bin/spark-submit examples/src/main/python/ml/train_validation_split.py
"""

if __name__ == "__main__":
    sc = SparkContext(appName="TrainValidationSplit")
    sqlContext = SQLContext(sc)
    # $example on$
    # Prepare training and test data.
    data = sqlContext.read.format("libsvm")\
        .load("data/mllib/sample_linear_regression_data.txt")
    train, test = data.randomSplit([0.7, 0.3])
    lr = LinearRegression(maxIter=10, regParam=0.1)

    # We use a ParamGridBuilder to construct a grid of parameters to search over.
    # TrainValidationSplit will try all combinations of values and determine best model using
    # the evaluator.
    paramGrid = ParamGridBuilder()\
        .addGrid(lr.regParam, [0.1, 0.01]) \
        .addGrid(lr.elasticNetParam, [0.0, 0.5, 1.0])\
        .build()

    # In this case the estimator is simply the linear regression.
    # A TrainValidationSplit requires an Estimator, a set of Estimator ParamMaps, and an Evaluator.
    tvs = TrainValidationSplit(estimator=lr,
                               estimatorParamMaps=paramGrid,
                               evaluator=RegressionEvaluator(),
                               # 80% of the data will be used for training, 20% for validation.
                               trainRatio=0.8)

    # Run TrainValidationSplit, and choose the best set of parameters.
    model = tvs.fit(train)
    # Make predictions on test data. model is the model with combination of parameters
    # that performed best.
    prediction = model.transform(test)
    for row in prediction.take(5):
        print(row)
    # $example off$
    sc.stop()
