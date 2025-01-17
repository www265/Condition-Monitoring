import numpy as np
from sklearn.decomposition import PCA, KernelPCA, FactorAnalysis, TruncatedSVD, FastICA
from sklearn.manifold import TSNE, MDS, LocallyLinearEmbedding
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.datasets import load_iris, load_digits, load_wine
from sklearn.neural_network import BernoulliRBM
from sklearn.pipeline import Pipeline
from scipy.stats import zscore
import json
import logging
import matplotlib.pyplot as plt
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.models import Model


# Configure logging
logging.basicConfig (level=logging.DEBUG)


class DimentionReduction:
    def __init__(self):
        self.supported_datasets = ['iris', 'digits', 'wine']
        self.supported_algorithms = [
            'PCA', 'LDA', 'KernelPCA', 'ICA', 'FA',
            'tSNE', 'MDS', 'LLE', 'SVD', 'Autoencoder'
        ]

    def load_dataset(self, dataset_name):
        if dataset_name == 'iris':
            data = load_iris ()
        elif dataset_name == 'digits':
            data = load_digits ()
        elif dataset_name == 'wine':
            data = load_wine ()
        else:
            raise ValueError ("Unsupported dataset")

        X = data.data
        y = data.target
        feature_names = data.feature_names if hasattr (data, 'feature_names') else [f'feature_{i}' for i in
                                                                                    range (X.shape[1])]
        target_names = data.target_names if hasattr (data, 'target_names') else list (set (y))

        return X, y, feature_names, target_names

    def pca(self, X, n_components=2):
        scaler = StandardScaler ()
        X_scaled = scaler.fit_transform (X)
        model = PCA (n_components=n_components)
        reduced_data = model.fit_transform (X_scaled)
        return reduced_data

    def lda(self, X, y, n_components=2):
        model = LinearDiscriminantAnalysis (n_components=n_components)
        reduced_data = model.fit_transform (X, y)
        return reduced_data

    def kernel_pca(self, X, n_components=2, kernel='rbf'):
        scaler = StandardScaler ()
        X_scaled = scaler.fit_transform (X)
        model = KernelPCA (n_components=n_components, kernel=kernel)
        reduced_data = model.fit_transform (X_scaled)
        return reduced_data

    def ica(self, X, n_components=2):
        model = FastICA (n_components=n_components, random_state=0)
        reduced_data = model.fit_transform (X)
        return reduced_data

    def factor_analysis(self, X, n_components=2):
        model = FactorAnalysis (n_components=n_components, random_state=0)
        reduced_data = model.fit_transform (X)
        return reduced_data

    def tsne(self, X, n_components=2, perplexity=30):
        model = TSNE (n_components=n_components, perplexity=perplexity, random_state=0)
        reduced_data = model.fit_transform (X)
        return reduced_data

    def mds(self, X, n_components=2):
        model = MDS (n_components=n_components, random_state=0)
        reduced_data = model.fit_transform (X)
        return reduced_data

    def lle(self, X, n_components=2, n_neighbors=10):
        model = LocallyLinearEmbedding (n_neighbors=n_neighbors, n_components=n_components, eigen_solver='auto')
        reduced_data = model.fit_transform (X)
        return reduced_data

    def svd(self, X, n_components=2):
        model = TruncatedSVD (n_components=n_components, random_state=0)
        reduced_data = model.fit_transform (X)
        return reduced_data

    def autoencoder(self, X, n_components=2, n_hidden_layers=1, hidden_layer_size=128):
        # 移除此函数中的所有 logging 和数据标准化部分，
        # 因为这些步骤应该在 apply_dimentionality_reduction 函数中完成。
        input_dim = X.shape[1]
        autoencoder, encoder = self.create_autoencoder (input_dim, n_components, n_hidden_layers, hidden_layer_size)
        autoencoder.fit (X, X, epochs=50, batch_size=256, shuffle=True, validation_split=0.2, verbose=0)
        reduced_data = encoder.predict (X)
        return reduced_data

    def create_autoencoder(self, input_dim, encoding_dim, n_hidden_layers, hidden_layer_size):
        input_layer = Input (shape=(input_dim,))
        encoded = Dense (hidden_layer_size, activation='relu') (input_layer)
        for _ in range (n_hidden_layers - 1):
            encoded = Dense (hidden_layer_size, activation='relu') (encoded)
        encoded_output = Dense (encoding_dim, activation='relu') (encoded)

        decoded = Dense (hidden_layer_size, activation='relu') (encoded_output)
        for _ in range (n_hidden_layers - 1):
            decoded = Dense (hidden_layer_size, activation='relu') (decoded)
        decoded_output = Dense (input_dim, activation='sigmoid') (decoded)

        autoencoder = Model (inputs=input_layer, outputs=decoded_output)
        encoder = Model (inputs=input_layer, outputs=encoded_output)

        autoencoder.compile (optimizer='adam', loss='mean_squared_error')

        return autoencoder, encoder

    def apply_dimentionality_reduction(self, algorithm, dataset_name, parameters={}):
        X, y, _, target_names = self.load_dataset(dataset_name)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Convert numpy types to python native types for target_names
        target_names = [str(name) for name in target_names]

        if algorithm == 'Autoencoder':
            reduced_data = self.autoencoder(X_scaled, **parameters)
            dimensions = ['Dimension 1', 'Dimension 2']
        else:
            reducer = self._get_reducer(algorithm, parameters)
            reduced_data = reducer.fit_transform(X_scaled)

        # Ensure conversion to list before returning the result
        reduced_data_list = reduced_data.tolist() if isinstance(reduced_data, np.ndarray) else reduced_data

        # Determine the number of dimensions based on the type of reduced_data
        if isinstance(reduced_data, np.ndarray):
            num_dimensions = reduced_data.shape[1]
        elif isinstance(reduced_data, list):
            num_dimensions = len(reduced_data[0]) if reduced_data and isinstance(reduced_data[0], list) else 1
        else:
            raise TypeError("Unsupported data type for reduced_data")

        dimensions = [f'Dimension {i + 1}' for i in range(num_dimensions)]

        return {
            'data': reduced_data_list,
            'dimensions': dimensions,
            'targets': y.tolist(),  # Ensure conversion to list
            'target_names': target_names  # Use the converted target_names
        }

    def _get_reducer(self, algorithm, parameters):
        """Helper method to get the reducer based on the algorithm."""
        reducers = {
            'PCA': PCA,
            'LDA': LinearDiscriminantAnalysis,
            'KernelPCA': KernelPCA,
            'ICA': FastICA,
            'FA': FactorAnalysis,
            'tSNE': TSNE,
            'MDS': MDS,
            'LLE': LocallyLinearEmbedding,
            'SVD': TruncatedSVD,
        }
        if algorithm not in reducers:
            raise ValueError (f"Algorithm '{algorithm}' not supported.")

        n_components = parameters.pop ('n_components', 2)
        if algorithm == 'LDA':
            n_classes = len (np.unique (y))
            n_components = min (n_classes - 1, n_components)

        return reducers[algorithm] (n_components=n_components, **parameters)