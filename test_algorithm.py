from qgis.core import (
    QgsFeatureSink,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
)

class test_algorithm(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def name(self) -> str:
        return 'testing_algorithm'
    
    def displayName(self) -> str:
        return 'Testing Algorithm'
    
    def group(self) -> str:
        return 'Testing Algorithms'
    
    def groupId(self) -> str:
        return 'testing_algorithms'
    
    def shortHelpString(self) -> str:
        return 'This is a testing algorithm.'
    
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                'Input layer',
                [QgsProcessing.SourceType.TypeVectorAnyGeometry],
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, 'Output Layer')
        )

    def processAlgorithm(
            self,
            parameters,
            context,
            feedback,
    ):
        source = self.parameterAsSource(parameters, self.INPUT, context)

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            source.fields(),
            source.wkbType(),
            source.sourceCrs(),
        )

        features = source.getFeatures()

        for _, feature in enumerate(features):
            sink.addFeature(feature, QgsFeatureSink.Flag.FastInsert)

        return {self.OUTPUT: dest_id}
    
    def createInstance(self):
        return self.__class__()