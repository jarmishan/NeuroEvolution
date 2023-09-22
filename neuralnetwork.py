import numpy as _numpy

#activation functions for linear separability
activation_functions = {
    "tanh": (lambda x: _numpy.tanh(x), lambda x: 1 - x ** 2),
    "sigmoid": (lambda x: 1 / (1 + _numpy.exp(-x)), lambda x: x * (1 - x)),
    "relu": (lambda x: _numpy.maximum(x, 0), lambda x: _numpy.where(x>0, 1, 0))
}

class Dense:
    """A class to represent a fully connected layer in a neural network."""

    def __init__(self, input_size: int, output_size: int, activation: str) -> None:
        """
        Initialize a layer of the neural network.

        Args:
            input_size (int): The number of input neurons.
            output_size (int): The number of output neurons.
            activation (str): The name of a linearly separable function.
        """

        self.weights = _numpy.random.randn(output_size, input_size)
        self.biases = _numpy.random.randn(output_size, 1)

        self.activation, self.activation_derivative = activation_functions[activation.lower()]


    def forward_pass(self, inputs: _numpy.ndarray) -> None:
        """
        Preforms forward propagation.

        Args:
            inputs (numpy.ndarray): the input to this layer.

        Returns
            self.output(numpy.ndarray): the dot product of the inputs matrix and the weights matrix added to the biases vector.
        """

        self.inputs = inputs
        self.outputs = self.activation((_numpy.dot(self.weights, self.inputs) + self.biases))
        return self.outputs


    def backward_pass(self, output_gradient: _numpy.ndarray, learning_rate: float) -> None:
        """
        Perform backward propagation.

        Args:
            output_gradient (numpy.ndarray): The rate of change of the output with respect to its input.
            learning_rate (float): The amount the model should change in response to the error.

        Returns:
            numpy.ndarray: The gradient of the error with respect to the input
        """

        output_gradient *= self.activation_derivative(self.outputs)
        self.weights -= learning_rate * _numpy.dot(output_gradient, self.inputs.T)
        self.biases -= learning_rate * output_gradient

        return _numpy.dot(self.weights.T, output_gradient)



class NeuralNetwork:
    """A class to represent a sequential neural network."""

    def __init__(self, *layers) -> None:
        """
        Initializes the neural network with the specified layers.

        Args:
            *layers: A list of layer instances forming the neural network.
        """

        self.network = layers

    def _mean_squared_error_derivative(self, correct, prediction) -> _numpy.ndarray:
        """
        Computes the derivative of mean squared error.

        Args:
            correct (numpy.ndarray): The correct output.
            prediction(numpy.ndarray): The predicted output.

        Returns:
            float : The derivative of the mean squared error.
        """

        return 2 * _numpy.mean(prediction - correct)

    def forward_propagation(self, inputs) -> _numpy.ndarray:
        """
        Performs forward propagation through the network.

        Args:
            inputs: The input data.

        Returns:
            numpy.ndarray: The output after forward propagation.
        """

        output = inputs

        for layer in self.network:
            output = layer.forward_pass(output)

        return output

    def _back_propagation(self, output, answer, learning_rate) -> _numpy.ndarray:
        """
        Backpropagates the error through the network.

        Args:
            output (numpy.ndarray): The output of the network.
            answer (numpy.ndarray): The expected output.
            learning_rate (float): The amount the model should change in response to the error.. Defaults to 0.1.
        """

        gradient = self._mean_squared_error_derivative(answer, output)

        for layer in reversed(self.network):
            gradient = layer.backward_pass(gradient, learning_rate)


    def train(self, training_inputs, training_anwsers, epochs, *, learning_rate=0.1, display=False) -> None:
        """
        Trains the neural network using the specified inputs and answers.

        Args:
            training_inputs  (numpy.ndarray): The input data for training.
            training_answers  (numpy.ndarray): The expected output data for training.
            epochs (int): The number of training epochs.
            learning_rate (float, optional): The amount the model should change in response to the error.. Defaults to 0.1.
            display (bool, optional): Whether to display progress. Defaults to False.
        """

        for epoch in range(epochs):

            for inputs, answer in zip(training_inputs, training_anwsers):

                output = self.forward_propagation(inputs)
                self._back_propagation(output, answer, learning_rate)

            if display:
                print(f"{epoch + 1} / {epochs}")



class NeuroEvoloution(NeuralNetwork):
    """A subclass of NeuralNetwork that implements evolutionary algorithms for optimization."""

    def _mutate_layer(self, matrix: _numpy.ndarray, amount: float) -> _numpy.ndarray:
        """
        Mutates the weights or biases matrx by a specified amount.

        Args:
            matrix (numpy.ndarray): The weights or biases matrix to be mutated.
            amount (float): The mutation amount.

        Returns:
            numpy.ndarray: The mutated matrixes.
        """

        mutation_factor = _numpy.random.rand(*matrix.shape) * 2 - 1
        mutation = (mutation_factor) * amount

        return mutation

    def mutate(self, mutation_rate=0.25) -> None:
        """
        Mutates the weights and biases of the layers in the neural network.

        Args:
            mutation_rate (float, optional): The rate at which mutation occurs. Defaults to 0.25.
        """

        for layer in self.network:
            layer.weights += self._mutate_layer(layer.weights, mutation_rate)
            layer.biases += self._mutate_layer(layer.biases, mutation_rate)


    def crossover(self, parent: NeuralNetwork) -> None:
        """
        Performs a crossover operation with another neural network.

        Args:
            parent (NeuroEvolution): The neural network to perform crossover with.
        """

        for layer, parent_layer in zip(self.network, parent.network):
            layer.weights = (layer.weights + parent_layer.weights) / 2
            layer.biases = (layer.biases + parent_layer.biases) / 2


    def save(self, path: str) -> None:
        """
        Saves the neural network weights and biases to a .npz file.

        Args:
            path (str): The file path to save the weights and biases.
        """

        data = {}

        for level, layer in enumerate(self.network):
            data[f'layer{level}_weights'] = layer.weights
            data[f'layer{level}_biases'] = layer.biases

        _numpy.savez(path, **data)


    def load(self, path: str) -> None:
        """
        Loads the neural network weights and biases from a file.

        Args:
            path (str): The file path to load the weights and biases from.
        """

        path += ".npz"
        model = _numpy.load(path)

        for level, layer in enumerate(self.network):
            layer.weights = model[f'layer{level}_weights']
            layer.biases = model[f'layer{level}_biases']