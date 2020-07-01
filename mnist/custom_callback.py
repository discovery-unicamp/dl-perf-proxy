# Class to take the iteration time for each 10 iterations

import keras
from keras.callbacks import Callback
import time

class CountTime(Callback):
        def __init__(self,
                        final_time = 0.0,
                        init_time = 0.0,
                        init_time_per_step = 0.0,
                        count=1,
                        first_two = True,
                        val_init_time = 0.0,
                        first_valid = True):

                self.count = count
                self.final_time = final_time
                self.init_time = init_time
                self.init_time_per_step = init_time_per_step
                self.first_two = first_two
                self.val_init_time = val_init_time
                self.first_valid = first_valid

        def on_train_batch_begin(self, batch, logs=None):
            on_train_batch_begin_time = time.time()
            print('\non_train_batch_begin: {:6f}s'.format(on_train_batch_begin_time))
            if self.count > 1:
                self.final_time = on_train_batch_begin_time - self.init_time
                print('\n{} step training time: {:6f}s'.format(self.count-1, self.final_time))
            self.init_time = on_train_batch_begin_time
            self.count = self.count + 1
        def on_train_batch_end(self, batch, logs=None):
            on_train_batch_end_time = time.time()
            print('\non_train_batch_end: {:6f}s'.format(on_train_batch_end_time))
        def on_epoch_begin(self, epoch, logs=None):
            on_epoch_begin_time = time.time()
            print('\non_epoch_begin: {:6f}s'.format(on_epoch_begin_time))
            self.first_two = True
            self.count = 1

        def on_epoch_end(self, epoch, logs=None):
            end_time = time.time()
            print('\non_epoch_end: {:6f}s'.format(end_time))
            validation_time = end_time - self.val_init_time
            print("\nValidation time: {:6f}s".format(validation_time))
            print('\nReal time: {:6f}s'.format(end_time))
            self.first_valid = True
            self.first_two = True
            self.count = 1



        def on_test_batch_begin(self, batch, logs=None):

                """Called at the beginning of a batch in `evaluate` methods.

                Also called at the beginning of a validation batch in the `fit` methods,
                if validation data is provided.

                Subclasses should override for any actions to run.

                # Arguments
                        batch: integer, index of batch within the current epoch.
                        logs: dict, has keys `batch` and `size` representing the current
                                batch number and the size of the batch.
                """

                if self.first_valid:
                    on_test_batch_begin_time = time.time()
                    print('\non_test_batch_begin: {:6f}s'.format(on_test_batch_begin_time))
                    self.final_time = on_test_batch_begin_time - self.init_time
                    print('\n{} step training time: {:6f}s'.format(self.count-1, self.final_time))
                    self.val_init_time = time.time()
                    self.first_valid = False

class IterTime(Callback):
        def __init__(self,
                count = 0,
                final_time = 0.0,
                init_time = 0.0,
                ):

                self.count = count
                self.final_time = final_time
                self.init_time = init_time
        def on_batch_begin(self, batch, logs=None):
                if self.count > 0:
                        self.final_time = time.time() - self.init_time
                        print('\n{} step training time: {}s'.format(self.count, self.final_time))
                        print('\nReal time: {}'.format(time.time()))

                self.init_time = time.time()

                self.count = self.count + 1

class EpochTime(Callback):
        def __init__(self,
                final_time = 0.0,
                init_time = 0.0):

                self.final_time = final_time
                self.init_time = init_time

        def on_epoch_begin(self, epoch, logs=None):
                print('\nReal time: {}'.format(time.time()))
                self.init_time = time.time()


        def on_epoch_end(self, epoch, logs=None):

                self.final_time = time.time() - self.init_time
                print('\nEpoch time: {}s'.format(self.final_time))
