# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 10:05:11 2019

@author: ariele

Questo modulo contiene solamente le architetture di reti neurali che richiamo.
ritorna il modello costruito che poi va trainato nell'altro script
"""

from keras.models import Sequential
from keras.layers import Dense, Dropout, Bidirectional
from keras.layers import LSTM, GRU, SimpleRNN
from tensorflow.keras.wrappers.scikit_learn import KerasRegressor

from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer, r2_score, mean_squared_error

from sklearn.utils.validation import check_array

import numpy as np

def mean_absolute_percentage_error(y_true, y_pred):
    """Custom function to calculate mean absolute percentage error (MAPE)"""
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

def r2_score_3d(y_true, y_pred):

    try:
        y_true_flat = check_array(y_true, ensure_2d=False)
        y_pred_flat = check_array(y_pred, ensure_2d=False)
    except:
        y_true_flat = np.reshape(y_true, (y_true.shape[0],-1))
        y_pred_flat = np.reshape(y_pred, (y_pred.shape[0],-1))

    # Check if the shapes are compatible
    if y_true_flat.shape != y_pred_flat.shape:
        raise ValueError("Shapes of y_true and y_pred must be the same.")

    # Calculate R2 score for each output
    r2_per_output = [r2_score(y_true_flat[:, i], y_pred_flat[:, i]) for i in range(y_true_flat.shape[1])]

    # Combine the results (e.g., average or sum)
    final_score = np.mean(r2_per_output)

    return final_score

class Deep_learning():

    def __init__(self, optimizer, loss, scorer=None, epochs=None):
        if scorer == 'rmse':
            self.scoring = make_scorer(mean_squared_error, squared=False)  # Create RMSE scorer
        elif scorer == 'mse':
            self.scoring = make_scorer(mean_squared_error, squared=True)  # Create MSE scorer
        elif scorer == 'r2':
            self.scoring = make_scorer(r2_score_3d)  # Create R2 scorer
        elif scorer == 'mape':
            self.scoring = make_scorer(mean_absolute_percentage_error)  # Create R2 scorer
        else:
            self.scoring = None
        
        self.loss = loss
        self.optimizer = optimizer
        self.scorer = scorer
        self.epochs = epochs

    def FeedForward(self, train_X, n_output, n_node, act_function):

        n_layer = len(n_node)

        model = Sequential()      
        model.add(Dense(n_node[0], input_shape=(train_X.shape[1],train_X.shape[2]), activation=act_function))  
        for i in range(n_layer-1):                                              
            model.add(Dense(n_node[i+1], activation=act_function))
        model.add(Dense(n_output, activation=act_function))
        model.compile(optimizer=self.optimizer, loss=self.loss)
        model.summary()
        return model
    
    def FeedForward_gs(self, train_X, train_y, param_grid, 
                                batch_size=1, validation_data=None, validation_split=None):
        keras_regressor = KerasRegressor(
            build_fn=Deep_learning(
                self.optimizer,
                self.loss,
                self.scorer,
                self.epochs
            ).FeedForward, 
            train_X=train_X, n_output=param_grid['n_output'],
            epochs=self.epochs, batch_size=batch_size,
            validation_data=validation_data, validation_split=validation_split)
        self.gs_model = GridSearchCV(estimator=keras_regressor, param_grid=param_grid, scoring=self.scoring, cv=5)

        self.gs_model.fit(train_X, train_y, validation_data=validation_data, validation_split=validation_split)
        return self.gs_model.cv_results_

    # def fit_and_evaluate(self, train_X, n_output, n_node, act_function, train_y, validation_data=None):
    #     model = self.FeedForward(train_X, n_output, n_node, act_function)
    #     history = model.fit(train_X, train_y, epochs=self.epochs, batch_size=1, validation_data=validation_data)
    #     return history, model

    # def grid_search(self, train_X, train_y, param_grid=None,
    #                 validation_data=None, validation_split=0.8):
    #     results = []

    #     n_outputs = param_grid['n_output']
    #     n_nodes = param_grid['n_node']
    #     act_functions = param_grid['act_function']

    #     for n_output in n_outputs:
    #         for n_node in n_nodes:
    #             for act_function in act_functions:

    #                 history, model = self.fit_and_evaluate(train_X, n_output, n_node, act_function, train_y, validation_data=validation_data)
            
    #                 # You can use metrics from the history or model evaluation to select the best parameters
    #                 # For example, you might use val_loss or val_accuracy
    #                 # Here, I'm using the last validation loss as a metric
    #                 val_loss = history.history['loss'][-1]

    #                 results.append({
    #                     'n_outputs': n_output, 
    #                     'n_nodes': n_node, 
    #                     'act_functions': act_function, 
    #                     'val_loss': val_loss, 
    #                     'model': model})

    #     # Sort results based on validation loss (or other metric)
    #     results.sort(key=lambda x: x['val_loss'])

    #     return results
    
    # def FeedForward_grid_search(self, train_X, train_y, param_grid, batch_size=1, validation_data=None, validation_split=None):
    #     keras_regressor = KerasRegressor(
    #         build_fn=Deep_learning().FeedForward, train_X=train_X, train_y=train_y, n_output=param_grid['n_output'],
    #         optimizer=self.optimizer, loss=self.loss, epochs=self.epochs,
    #         batch_size=batch_size, validation_data=validation_data, validation_split=validation_split)
    #     self.gs_model = GridSearchCV(estimator=keras_regressor, param_grid=param_grid, scoring=self.scoring, cv=None)
    #     return self.gs_model
    
    # def FeedForward_grid_search(self, train_X, train_y, param_grid, batch_size=1, validation_data=None, validation_split=None):
    #     keras_regressor = KerasRegressor(
    #         build_fn=self.FeedForward, train_X=train_X, n_output=param_grid['n_output'],
    #         epochs=self.epochs, batch_size=batch_size)
           
    #     self.gs_model = GridSearchCV(estimator=keras_regressor, param_grid=param_grid, scoring=self.scoring)
    #     self.gs_model.fit(
    #         train_X, train_y, epochs=self.epochs, batch_size=batch_size, validation_split=validation_split)
    #     return self.gs_model

# Example usage:
# deep_learning = DeepLearning(optimizer='adam', loss='mean_squared_error', epochs=10, scoring='r2')
# grid_search_param_grid = {'n_output': [1, 2, 3]}  # Add other hyperparameters as needed
# grid_search_model = deep_learning.FeedForward_grid_search(train_X, grid_search_param_grid, validation_split=0.2)

# class Deep_learning():
    
#     def __init__(self):
#         pass
    
    # """Funzione per generare il modello deep neural network. La selezione 
    # avviene a seconda della stringa data nella function di train-test"""  
    # def Deep_learning_model(self, model_type, train_X,  n_node, n_layer, n_output,
    #                         act_function=None, bagging_cicle=None):
    #     self.model_type = model_type
    #     # =============================================================================
    #     #         #Classic feed_foraward ANN
    #     # =============================================================================
    #     if self.model_type=='Feed_forward':
    #         self.model = Sequential()      
    #         self.model.add(Dense(n_node[0], input_shape=(train_X.shape[1],train_X.shape[2]),
    #                              activation=act_function))  
    #         for i in range(n_layer-1):                                              
    #             self.model.add(Dense(n_node[i+1], activation=act_function))
    #         self.model.add(Dense(n_output, activation=act_function))
    #         self.model.summary()
        
#         # =============================================================================
#         #         #Classic Long short-term memory
#         # =============================================================================
#         elif self.model_type=='Lstm':
#             self.model = Sequential()
#             self.model.add(LSTM(n_node[0],  return_sequences=True, 
#                                 input_shape=(train_X.shape[1],
#                                              train_X.shape[2])))
#             for i in range (n_layer-2):
#                 self.model.add(LSTM(n_node[i+1], return_sequences=True)) 
#             self.model.add(LSTM(n_node[-1]))
#             self.model.add(Dense(n_output))
#             self.model.summary()
        
#         # =============================================================================
#         #         #Classic Gated recurrent unit
#         # =============================================================================
#         elif self.model_type=='GRU':
#             self.model = Sequential()
#             self.model.add(GRU(n_node[0],  return_sequences=True, 
#                                 input_shape=(train_X.shape[1],
#                                              train_X.shape[2])))
#             for i in range (n_layer-2):
#                 self.model.add(GRU(n_node[i+1], return_sequences=True)) 
#             self.model.add(GRU(n_node[-1]))
#             self.model.add(Dense(n_output))
#             self.model.summary()
         
#         # =============================================================================
#         #         #Classic Elman Recurren neural network
#         # =============================================================================
#         elif self.model_type=='ERNN':
#             self.model = Sequential()
#             self.model.add(SimpleRNN(n_node[0],  return_sequences=True, 
#                                 input_shape=(train_X.shape[1],
#                                              train_X.shape[2])))
#             for i in range (n_layer-2):
#                 self.model.add(SimpleRNN(n_node[i+1], return_sequences=True)) 
#             self.model.add(SimpleRNN(n_node[-1]))
#             self.model.add(Dense(n_output))
#             self.model.summary()
          
#         # =============================================================================
#         #         # Bidirectional LSTM     
#         # =============================================================================
#         elif self.model_type=='bidirectional_Lstm':
#             self.model = Sequential()  
#             self.model.add(Bidirectional(LSTM(n_node[0], return_sequences=True),
#                                          input_shape=(train_X.shape[1],
#                                                       train_X.shape[2])))
#             for i in range (n_layer-2):
#                 self.model.add(Bidirectional(LSTM(n_node[i+1], return_sequences=True))) 
#             self.model.add(Bidirectional(LSTM(n_node[-1])))
#             self.model.add(Dense(1))  
#             self.model.summary()
            
#         # =============================================================================
#         #         # LSTM x2 + ANN x2    
#         # =============================================================================
#         elif self.model_type=='Mixture1':
#             self.model = Sequential()
#             self.model.add(LSTM(n_node,  return_sequences=True, 
#                                 input_shape=(train_X.shape[1],
#                                              train_X.shape[2])))
#             self.model.add(LSTM(n_node)) 
#             self.model.add(Dense(n_node, activation='relu'))
#             self.model.add(Dense(n_node, activation='relu'))
#             self.model.add(Dense(1))
#             self.model.summary()
        
#         # =============================================================================
#         #         # ANN X2 + Lstm x2
#         # =============================================================================
#         elif self.model_type=='Mixture2':
#             self.model = Sequential()
#             self.model.add(Dense(n_node, input_shape=(train_X.shape[1],train_X.shape[2]),
#                                  activation=act_function))  
#             self.model.add(Dense(n_node, activation='relu'))
#             self.model.add(LSTM(n_node,  return_sequences=True, 
#                                 input_shape=(train_X.shape[1],
#                                              train_X.shape[2])))
#             self.model.add(LSTM(n_node,  return_sequences=True, 
#                                 input_shape=(train_X.shape[1],
#                                              train_X.shape[2])))
#             self.model.add(Dense(1))
#             self.model.summary()
            
#         # =============================================================================
#         #         # LSTM + ANN + LSTM + ANN
#         # =============================================================================
#         elif self.model_type=='Mixture3':
#             self.model = Sequential()
#             self.model.add(LSTM(n_node,  return_sequences=True, 
#                                 input_shape=(train_X.shape[1],
#                                              train_X.shape[2])))
#             self.model.add(Dense(n_node, activation='relu'))
#             self.model.add(LSTM(n_node, return_sequences=True)) 
#             self.model.add(Dense(n_node, activation='relu'))
#             self.model.add(Dense(1))
#             self.model.summary()

#         # =============================================================================
#         #         #  ANN + LSTM + ANN + LSTM
#         # =============================================================================
#         elif self.model_type=='Mixture4':
#             self.model = Sequential()
#             self.model.add(Dense(n_node, input_shape=(train_X.shape[1],train_X.shape[2]),
#                                  activation=act_function)) 
#             self.model.add(LSTM(n_node, return_sequences=True))
#             self.model.add(Dense(n_node, activation='relu'))
#             self.model.add(LSTM(n_node))
#             self.model.add(Dense(1))
#             self.model.summary()              
               
#         return self.model