import numpy

activation_functions = {
    "tanh": (lambda x: numpy.tanh(x), lambda x: 1 - x ** 2),
    "sigmoid": (lambda x: 1 / (1 + numpy.exp(-x)), lambda x: x * (1 - x)),
    "relu": (lambda x: numpy.maximum(x, 0), lambda x: numpy.where(x>0, 1, 0))
}

class Dense:
    def __init__(self, input_size, output_size, activation):
        self.activation, self.activation_derivative = activation_functions[activation.lower()]

        self.weights = numpy.random.randn(output_size, input_size)
        self.biases = numpy.random.randn(output_size, 1)


    def forward_pass(self, inputs):
        self.inputs = inputs
        self.outputs = self.activation((numpy.dot(self.weights, self.inputs) + self.biases))
        return self.outputs
        
    
    def backward_pass(self, output_gradiant, learning_rate):
        output_gradiant *= self.activation_derivative(self.outputs)
        self.weights -= learning_rate * numpy.dot(output_gradiant, self.inputs.T)
        self.biases -= learning_rate * output_gradiant

        return numpy.dot(self.weights.T, output_gradiant)
    

class NeuralNetwork:
    def __init__(self, *layers):
        self.network = layers


    def forward_propogation(self, inputs):
        output = inputs
        
        for layer in self.network:
            output = layer.forward_pass(output)

        return output
    

class NeuroEvoloution(NeuralNetwork):
    def mutate_layer(self, matrix, amount):
        mutation_factor = numpy.random.rand(*matrix.shape) * 2 - 1
        mutation = (mutation_factor) * amount

        return mutation
        
    def mutate(self, mutation_rate=0.25):
        for layer in self.network:
            layer.weights += self.mutate_layer(layer.weights, mutation_rate)
            layer.biases += self.mutate_layer(layer.biases, mutation_rate)


    def crossover(self, parent):
        for layer, parent_layer in zip(self.network, parent.network):
            layer.weights = (layer.weights + parent_layer.weights) / 2
            layer.biases = (layer.biases + parent_layer.biases) / 2
            
            
    def save(self, path):
        data = {} 
        
        for level, layer in enumerate(self.network):
            data[f'layer{level}_weights'] = layer.weights
            data[f'layer{level}_biases'] = layer.biases
        
        numpy.savez(path, **data)
        

    def load(self, path):
        path += ".npz"
        model = numpy.load(path)
        
        for level, layer in enumerate(self.network):
            layer.weights = model[f'layer{level}_weights']
            layer.biases = model[f'layer{level}_biases']