import numpy as np
import pymc3 as pm
import pandas as pd
import pymc3 as pm
import numpy as np
import matplotlib.pyplot as plt

def norma(samples, desired_sum):
    return np.array([s/samples.sum()*desired_sum for s in samples])

import scipy.stats as stats
from scipy.optimize import minimize

class BetaDistribution:

    def __init__(self, data, initial_params) -> None:
        self.name = "Beta"
        self.data = data
        self.initial_params = initial_params
    
    def neg_log_likelihood(self, params):
        alpha, beta = params
        log_likelihood = -np.sum((alpha - 1) * np.log(self.data) + (beta - 1) * np.log(1 - self.data))
        return -log_likelihood

    def evaluate_best_params(self):
        bounds = [(0, np.inf), (0, np.inf)]
        result = minimize(
            self.neg_log_likelihood, self.initial_params, method='Nelder-Mead', 
            bounds=bounds, tol=0.5)
        
        alpha_hat, beta_hat = result.x
        if result.status == 0:
            self.alpha_hat = alpha_hat
            self.beta_hat = beta_hat
        else:
            # if (alpha_hat != np.NaN) or (beta_hat != np.NaN):
            #     self.alpha_hat = alpha_hat
            #     self.beta_hat = beta_hat
            # else:
            self.alpha_hat, self.beta_hat = self.initial_params
    
    def get_params(self):
        return {"alpha":self.alpha_hat, "beta":self.beta_hat}

    def get_pm_fct(self):
        return pm.Beta

class BinomialDistribution:

    def __init__(self, data, initial_params) -> None:
        self.name = "Binomial"
        self.data = data
        self.initial_params = initial_params
    
    def neg_log_likelihood(self, params):

        from scipy.special import i0

        mu, kappa = params
        log_likelihood = -np.sum(np.log(2 * np.pi * i0(kappa)) + kappa * np.cos(self.data - mu))
        return -log_likelihood

    def evaluate_best_params(self):
        result = minimize(self.neg_log_likelihood, self.initial_params, method='Nelder-Mead', tol=self.initial_params[0]/self.initial_params[1])
        mu_hat, kappa_hat = result.x

        if result.status == 0:
            self.mu_hat = mu_hat
            self.kappa_hat = kappa_hat
        else:
            # if (mu_hat != np.NaN) or (kappa_hat != np.NaN):
            #     self.mu_hat = mu_hat
            #     self.kappa_hat = kappa_hat
            # else:
            self.mu_hat, self.kappa_hat = self.initial_params
    
    def get_params(self):
        return {"n":self.mu_hat, "p":self.kappa_hat}
    
    def get_pm_fct(self):
        return pm.Binomial

class Chi2Distribution:

    def __init__(self, data, initial_params) -> None:
        self.name = "ChiSquare"
        self.data = data
        self.initial_params = initial_params

    def neg_log_likelihood(self, params):

        from scipy.special import gammaln

        k = params
        log_likelihood = -np.sum((k / 2 - 1) * np.log(self.data) - (self.data / 2) - k / 2 * np.log(2) - gammaln(k / 2))
        return -log_likelihood

    def evaluate_best_params(self):
        result = minimize(self.neg_log_likelihood, self.initial_params, method='Nelder-Mead', tol=1)
        k_hat = result.x

        if result.status == 0:
            self.k_hat = k_hat[0]
        else:
            # if (k_hat != np.NaN):
            #     self.k_hat = k_hat[0]
            # else:
            self.k_hat = self.initial_params[0]
    
    def get_params(self):
        return {"nu":self.k_hat}
    
    def get_pm_fct(self):
        return pm.ChiSquared
    
class NormalDist:

    def __init__(self, data, initial_params) -> None:
        self.name = "Normal"
        self.data = data
        self.initial_params = initial_params
    
    def neg_log_likelihood(self, params):
        mu, sigma = params
        log_likelihood = -np.sum(np.log(np.sqrt(2*np.pi*sigma**2)) - (self.data-mu)**2 / (2*sigma**2))
        return -log_likelihood

    def evaluate_best_params(self):
        result = minimize(self.neg_log_likelihood, self.initial_params, method='Nelder-Mead', tol=self.initial_params[0]/self.initial_params[1])
        mu_hat, sigma_hat = result.x

        ## substitute the sigma_hat with the original
        sigma_hat = self.data.std()

        if result.status == 0:
            self.mu_hat = mu_hat
            self.sigma_hat = sigma_hat
        else:
            if (mu_hat != np.NaN) or (sigma_hat != np.NaN):
                self.mu_hat = mu_hat
                self.sigma_hat = sigma_hat
            else:
                self.mu_hat, self.sigma_hat = self.initial_params
    
    def get_params(self):
        return {"mu":self.mu_hat, "sigma":self.sigma_hat}
    
    def get_pm_fct(self):
        return pm.Normal


class UniformDistribution:

    def __init__(self, data, initial_params) -> None:
        self.name = "Uniform"
        self.data = data
        self.initial_params = initial_params
    
    def neg_log_likelihood(self, params):
        a, b = params
        log_likelihood = -np.sum(np.log(b - a))
        return -log_likelihood

    def evaluate_best_params(self):
        result = minimize(self.neg_log_likelihood, self.initial_params, method='Nelder-Mead', tol=self.initial_params[0]/self.initial_params[1])
        a_hat, b_hat = result.x

        if result.status == 0:
            self.a_hat = a_hat
            self.b_hat = b_hat
        else:
            self.mu_hat, self.sigma_hat = self.initial_params
    
    def get_params(self):
        return {"a":self.a_hat, "b":self.b_hat}
    
    def get_pm_fct(self):
        return pm.Uniform

class VonMisesDistribution:

    def __init__(self, data, initial_params) -> None:
        self.name = "VonMises"
        self.data = data
        self.initial_params = initial_params

    def neg_log_likelihood(self, params):
        from scipy.special import i0
        mu, kappa = params
        log_likelihood = -np.sum(np.log(2 * np.pi * i0(kappa)) + kappa * np.cos(self.data - mu))
        return -log_likelihood

    def evaluate_best_params(self):
        bounds = [(None, None), (0.001, None)]
        result = minimize(
            self.neg_log_likelihood, self.initial_params, method='L-BFGS-B', bounds=bounds,
            tol=self.initial_params[0]/self.initial_params[1])
        mu_hat, kappa_hat = result.x
        if result.status == 0:
            self.mu_hat = mu_hat
            self.kappa_hat = kappa_hat
        else:
            # if (mu_hat != np.NaN) or (kappa_hat != np.NaN):
            #     self.mu_hat = mu_hat
            #     self.kappa_hat = sigma_hat
            # else:
            self.mu_hat, self.kappa_hat = self.initial_params
    
    def get_params(self):
        return {"mu":self.mu_hat, "kappa":self.kappa_hat}
    
    def get_pm_fct(self):
        return pm.VonMises
    
## distribution collector
class Distributions:

    def __init__(self, observed, add_all=False) -> None:
        self.observed = observed
        self.evaluate_hist()
        self.models = []
        if add_all == True:
            self.add_Beta()
            self.add_Binomial()
            self.add_Chi2()
            self.add_Normal()
            self.add_VonMises()
            self.add_Uniform()

    def evaluate_hist(self):
        self.observed_hist, self.bins = np.histogram(self.observed,bins='auto')
    
    def normalize_data(self):
        self.min_val = np.min(self.observed)
        self.max_val = np.max(self.observed)
        self.normalized_data = (self.observed - self.min_val) / (self.max_val - self.min_val)

    def minimize_LH(distribution):
        return minimize(
            distribution.neg_log_likelihood, distribution.initial_params, 
            method='Nelder-Mead', tol=1)
    
    def generate_samples(self,n_samples=None):
        desired_sum = self.observed.sum()

        if n_samples == None:
            n_samples = len(self.observed)
        self.samples = []
        for t in self.models:
            try:
                with pm.Model() as model:
                    model_name = t[1].name
                    params = t[1].get_params()
                    rv = t[0]("rv", **params)
                    sample = pm.sample_prior_predictive(n_samples)
                    sample = norma(sample["rv"], desired_sum)
                    if np.isnan(sample).any():
                        continue
                    self.samples.append((t[1],sample))
            except:
                continue
 
        return self.samples

    def execute_chi2test(self):

        from scipy.stats import chisquare

        samples_gen = self.generate_samples()
        
        best_p_value = 0
        
        self.chi2test_df = pd.DataFrame()
        names = []
        chi2_stats = []
        p_values = []
        for s in samples_gen:
            chi2_stat, p_value = chisquare(self.observed, f_exp=s[1])
            names.append(str(s[0].name))
            chi2_stats.append(chi2_stat)
            p_values.append(p_value)
            if p_value >= best_p_value:
                self.best_model = s[0]

        self.chi2test_df["name"] = names
        self.chi2test_df["chi2_stat"] = chi2_stats
        self.chi2test_df["p_value"] = p_values

        return self.best_model
    
    def plot_distributions(self, path):

        for s in self.samples:
            distribution_name = str(s[0])
            plt.hist(s[1], label=distribution_name, bins='auto', color="cyan")
            plt.hist(self.observed, bins='auto', color='orange')
            plt.savefig(path+distribution_name+".png")
            plt.close()

    def add_Beta(self):

        mu = self.observed.mean()
        sigma = self.observed.std()
        
        d = BetaDistribution(self.observed, [mu,sigma])
        d.evaluate_best_params() 

        self.models.append((pm.Beta, d))

    def add_Binomial(self):
        
        mu = self.observed.mean()
        sigma = self.observed.std()

        d = BinomialDistribution(self.observed, [mu,sigma])
        d.evaluate_best_params()

        self.models.append((pm.Binomial, d))
    
    def add_Chi2(self):
        
        mu = self.observed.mean()

        d = Chi2Distribution(self.observed, [mu])
        d.evaluate_best_params()

        self.models.append((pm.ChiSquared, d))

    def add_Normal(self):
        
        mu = self.observed.mean()
        sigma = self.observed.std()

        d = NormalDist(self.observed, [mu,sigma])
        d.evaluate_best_params()  

        self.models.append((pm.Normal, d))

    def add_Uniform(self):
        
        a = self.observed.min()
        b = self.observed.max()

        d = UniformDistribution(self.observed, [a,b])
        d.evaluate_best_params()  

        self.models.append((pm.Uniform, d))

    def add_VonMises(self):
        
        mu = self.observed.mean()
        sigma = self.observed.std()

        d = VonMisesDistribution(self.observed, [mu,sigma])
        d.evaluate_best_params()

        self.models.append((pm.VonMises, d))
            
# n_samples = 2000
# distr_type = 'normal'

############################################################

# if distr_type == 'beta':
#     data = stats.beta.rvs(a=2, b=5, size=n_samples)
    
# # elif distr_type == 'binomial':
# #     data = stats.binom.rvs(size=n_samples)

# elif distr_type == 'chisquared':
#     data = stats.chi2.rvs(10, size=n_samples)

# elif distr_type == 'exponential':
#     data = stats.expon.rvs(size=n_samples)

# elif distr_type == 'gamma':
#     data = stats.gamma.rvs(a=50, size=n_samples)

# elif distr_type == 'gumbel':
#     data = stats.gumbel_l.rvs(size=n_samples)

# elif distr_type == 'lognormal':
#     data = stats.lognorm.rvs(size=n_samples)

# elif distr_type == 'normal':
#     data = stats.norm.rvs(size=n_samples)

# elif distr_type == 'poisson':
#     data = stats.poisson.rvs(size=n_samples)

# elif distr_type == 'uniform':
#     data = stats.uniform.rvs(size=n_samples)

# elif distr_type == 'vonmises':
#     data = stats.vonmises.rvs(kappa=5, size=n_samples)

# elif distr_type == 'weibull':
#     data = stats.weibull_max.rvs(size=n_samples)

# plt.hist(data, bins='auto', color='orange')
# plt.show()
# plt.close()

##################################################################

# def params_Poisson(sample_data):

#     sample_data = np.array([ int(i) for i in sample_data ])

#     from scipy.optimize import minimize
#     from scipy.special import factorial

#     def neg_log_likelihood(param, data):
#         lambd = param[0]  # Access the parameter value from the array
#         log_likelihood = -np.sum(data * np.log(lambd) - lambd - np.log(factorial(data)))
#         return -log_likelihood

#     initial_param = [sample_data.mean()]  # Provide the initial parameter value as a list or array
#     bounds = [(0, None)]  # Lower bound of 0 for the rate parameter

#     result = minimize(neg_log_likelihood, initial_param, args=(sample_data,), bounds=bounds, method='L-BFGS-B')

#     lambda_hat = result.x[0]  # Access the estimated parameter value from the array

#     return lambda_hat
# def params_Gamma(sample_data):

#     from scipy.optimize import minimize
#     from scipy.special import gamma, digamma

#     def neg_log_likelihood(params, data):
#         alpha, beta = params
#         log_likelihood = -np.sum(alpha * np.log(beta) + (alpha - 1) * np.log(data) - beta * data - np.log(gamma(alpha)))
#         return -log_likelihood

#     initial_params = [sample_data.mean(), 1]
#     bounds = [(0, None), (0, None)]

#     result = minimize(
#         neg_log_likelihood, initial_params, args=(sample_data,), bounds=bounds, 
#         method='Nelder-Mead', options={"maxiter":100}, tol=sample_data.mean()/len(sample_data))

#     if result.status == 0:
#         alpha_hat, beta_hat = result.x
#     else:
#         alpha_hat, beta_hat = initial_params[0], initial_params[1]
#     return alpha_hat, beta_hat

# def params_Exp(sample_data):
#     from scipy.optimize import minimize

#     def neg_log_likelihood(param, data):
#         lambda_val = 1 / param
#         log_likelihood = -np.sum(np.log(lambda_val) + lambda_val * data)
#         return -log_likelihood

#     initial_param = sample_data.mean()

#     result = minimize(neg_log_likelihood, initial_param, args=(sample_data,), method='Nelder-Mead', tol=sample_data.mean()/len(sample_data))

#     lambda_hat = 1 / result.x
#     return lambda_hat[0]

# def params_Weibull(sample_data):

#     from scipy.optimize import minimize

#     def neg_log_likelihood(params, data):
#         k, lambda_val = params
#         log_likelihood = -np.sum(np.log(k/lambda_val) + ((data/lambda_val)**k) + np.log(data) - (data/lambda_val)**k)
#         return -log_likelihood

#     initial_params = [1, 1]
#     bounds = [(0, None), (0, None)]

#     result = minimize(neg_log_likelihood, initial_params, args=(sample_data,), bounds=bounds, method='L-BFGS-B')

#     k_hat, lambda_hat = result.x
#     return k_hat, lambda_hat

# def params_Lognormal(sample_data):

#     from scipy.optimize import minimize

#     def neg_log_likelihood(params, data):
#         mu, sigma = params
#         log_likelihood = -np.sum(np.log(sigma * np.sqrt(2 * np.pi)) + ((np.log(data) - mu) ** 2) / (2 * sigma ** 2))
#         return -log_likelihood

#     initial_params = [0, 1]
#     bounds = [(None, None), (0, None)]

#     result = minimize(neg_log_likelihood, initial_params, args=(sample_data,), bounds=bounds, method='L-BFGS-B')

#     mu_hat, sigma_hat = result.x
#     return mu_hat, sigma_hat
    
# def params_Gumbel(sample_data):

#     from scipy.optimize import minimize

#     def neg_log_likelihood(params, data):
#         loc, scale = params
#         log_likelihood = -np.sum(-(data - loc) / scale - np.exp(-(data - loc) / scale) - np.log(scale))
#         return -log_likelihood

#     initial_params = [sample_data.mean(), 1]
#     bounds = [(None, None), (0, None)]

#     result = minimize(neg_log_likelihood, initial_params, args=(sample_data,), bounds=bounds,
#                       method='Nelder-Mead', options={"maxiter":1000}, tol=sample_data.mean()/len(sample_data))
    
#     loc_hat, scale_hat = result.x
#     if result.status == 0:
#         return loc_hat, scale_hat
#     else:
#         if (loc_hat != np.NaN) or (scale_hat != np.NaN):
#             return loc_hat, scale_hat
#         else:
#             loc_hat, scale_hat = initial_params[0], initial_params[1]


# try:
# with pm.Model() as model:
# # Define parameters of the distribution
# if distribution == pm.Normal:
#     mu, sigma = params_Normal(obs_data)
#     param_args = {"mu": mu, "sigma": sigma}
# elif distribution == pm.Poisson:
#     mu = params_Poisson(obs_data)
#     param_args = {"mu": mu}
# elif distribution == pm.Binomial:
#     n = 50  # Number of trials (for binomial and Poisson distributions)
#     p = 0.5  # Probability of success (for binomial distribution)
#     param_args = {"n": n, "p": p}
# elif distribution == pm.Beta:
#     alpha, beta = params_Beta(obs_data)
#     param_args = {"alpha": alpha, "beta": beta}
# elif distribution == pm.Gamma:
#     alpha, beta = params_Gamma(obs_data)
#     param_args = {"alpha": alpha, "beta": beta}
# elif distribution == pm.Uniform:
#     lower = 0  # Lower bound (for uniform distribution)
#     upper = 1  # Upper bound (for uniform distribution)
#     param_args = {"lower": lower, "upper": upper}
# elif distribution == pm.Exponential:
#     lambda_hat = params_Exp(obs_data)
#     param_args = {"lam": lambda_hat}
# elif distribution == pm.Weibull:
#     k_hat, lambda_hat = params_Weibull(obs_data)
#     param_args = {"alpha": k_hat, "beta": lambda_hat}
# elif distribution == pm.LogNormal:
#     mu, sigma = params_Lognormal(obs_data)
#     param_args = {"mu": mu, "sigma": sigma}
# elif distribution == pm.VonMises:
#     mu, kappa = params_VonMises(obs_data)
#     param_args = {"mu": mu, "kappa": kappa}
# elif distribution == pm.Gumbel:
#     mu, beta = params_Gumbel(obs_data)
#     param_args = {"mu": mu, "beta": beta}
# elif distribution == pm.ChiSquared:
#     nu = params_ChiSquared(obs_data)
#     param_args = {"nu": nu}
# else:
#     param_args = {}  # No additional parameters


# a = pd.DataFrame(samples).T

# import matplotlib.pyplot as plt

# for i in a.iteritems():
#     try:
#         d = i[1].values
#         plt.hist(d, bins = np.arange(0,1,0.01)) 
#         plt.title("histogram") 
#         plt.show()
#     except:
#         continue

class Model:
    def __init__(self, model_idx, model=None, args=None, mu=None, sd=None, data=None) -> None:
        self.model_idx = model_idx
        self.model = model
        self.args = args
    
    def run(self):
        model_pm_type = self.model.get_pm_fct()
        params = self.model.get_params()
        return model_pm_type(self.model_idx, **params)
    
def get_traces(metered_value, models, model_weights=None):

    with pm.Model() as model:

        if model_weights is None:
            num_models = models.shape[0]
            # Prior probabilities for the models - INITIAL WEIGHTS
            model_weights = pm.Dirichlet('model_weights', a=np.ones(num_models))

        predictions = []
        for m_id in models.index:
            print(f"Model {m_id}")

            model = Model(model_idx=m_id, model=models.loc[m_id]["model_setup"])
            predictions.append(model.run())
        
        combined_prediction = pm.math.dot(model_weights, predictions)

        # Likelihood of the observed value
        likelihood = pm.Normal('observed', mu=combined_prediction, sd=1, observed=metered_value)
        
        # Perform model averaging
        trace = pm.sample(2000, tune=1000, cores=1, target_accept=0.9)  # MCMC sampling
        # trace = pm.sample(2000, tune=1000, cores=1, step=pm.HamiltonianMC())  # MCMC sampling
        # trace = pm.sample(2000, tune=1000, cores=4, step=pm.NUTS())  # MCMC sampling

        # Plot the posterior distribution of a parameter
        # pm.plot_posterior(trace, var_names=['model_weights'], hdi_prob=0.95)

        # Generate posterior predictive samples
        # posterior_predictive = pm.sample_posterior_predictive(trace, model=model, samples=500)

        return trace, likelihood




















observed_values = 3
ensemble_M1 = np.random.uniform(0.2,4,20)
ensemble_M2 = np.random.uniform(0.9,3.5,20)
ensemble_M3 = np.random.uniform(0.6,5.5,20)

models = pd.DataFrame(columns=["data","model_setup"], index=["M1","M2","M3"])

models["data"] = [ensemble_M1,ensemble_M2,ensemble_M3]

def run(data, show_data=False):
    data = norma(data, data.sum())

    plt.hist(data, bins='auto', color='orange')
    if show_data == True:
        plt.show()
    plt.close()

    dists = Distributions(data, add_all=True)
    best_model = dists.execute_chi2test()
    # dists.plot_distributions("/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/src/bin/uncertainty/plots/")

    return best_model

for m_id in models.index:
    best_model = run(models.loc[m_id]["data"])
    models.loc[m_id]["model_setup"] = best_model
    print(f"{m_id} is a {best_model.name} distribution.")


trace, lh_obs = get_traces(observed_values, models)

# Extract the posterior probabilities
model_weights_posterior = trace['model_weights']

# Compute the posterior means as the final weights
model_weights_mean = model_weights_posterior.mean(axis=0)

for i in range(models.shape[0]):
    print(f"Model {i+1} weight:", model_weights_mean[i])


print("OK")
## for each day
# read the superens_forecast.csv
## for each hour of the forecast
## for each model
# 1. extract the array of 20 elements
# 2. evaluate mean
# 3. evaluate sd
# 4. save in df

## df: datetime 001 002 003 004 005 006 ... 020
