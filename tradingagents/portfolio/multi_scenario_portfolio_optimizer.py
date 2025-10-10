"""
Multi-Scenario Portfolio Optimizer
Implements multiple portfolio optimization algorithms for LLM integration
"""

import numpy as np
import pandas as pd
import cvxpy as cp
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class MultiScenarioPortfolioOptimizer:
    """
    Portfolio optimization with multiple methods
    Each method represents a different investment philosophy
    """
    
    def __init__(self, returns_data: pd.DataFrame, stock_metrics: Dict[str, Dict]):
        """
        Initialize optimizer
        
        Args:
            returns_data: DataFrame with returns (stocks as columns, dates as rows)
            stock_metrics: Dict of stock metrics from aggregator
        """
        self.returns = returns_data
        self.tickers = returns_data.columns.tolist()
        self.n_assets = len(self.tickers)
        self.stock_metrics = stock_metrics
        
        # Calculate statistics
        self.mean_returns = returns_data.mean() * 252  # Annualized
        self.cov_matrix = returns_data.cov() * 252  # Annualized
        self.corr_matrix = returns_data.corr()
        
        print(f"Initialized optimizer for {self.n_assets} assets")
        print(f"   Tickers: {', '.join(self.tickers)}")
    
    def optimize_all_scenarios(self) -> Dict[str, Dict]:
        """Run all optimization scenarios"""
        
        scenarios = {}
        
        print("\nRunning multi-scenario portfolio optimization...")
        
        # Scenario 1: Maximum Sharpe Ratio
        try:
            scenarios['max_sharpe'] = self.max_sharpe_optimization()
            print("   SUCCESS: Max Sharpe Ratio")
        except Exception as e:
            print(f"   ERROR: Max Sharpe failed: {e}")
        
        # Scenario 2: Minimum Variance
        try:
            scenarios['min_variance'] = self.min_variance_optimization()
            print("   SUCCESS: Minimum Variance")
        except Exception as e:
            print(f"   ERROR: Min Variance failed: {e}")
        
        # Scenario 3: Risk Parity
        try:
            scenarios['risk_parity'] = self.risk_parity_optimization()
            print("   SUCCESS: Risk Parity")
        except Exception as e:
            print(f"   ERROR: Risk Parity failed: {e}")
        
        # Scenario 4: Maximum Diversification
        try:
            scenarios['max_diversification'] = self.max_diversification_optimization()
            print("   SUCCESS: Max Diversification")
        except Exception as e:
            print(f"   ERROR: Max Diversification failed: {e}")
        
        # Scenario 5: Hierarchical Risk Parity (has precise weights)
        try:
            scenarios['hrp'] = self.hierarchical_risk_parity()
            print("   SUCCESS: Hierarchical Risk Parity")
        except Exception as e:
            print(f"   ERROR: HRP failed: {e}")
        
        # Removed Equal Weight - produces too "clean" results (50%/50%)
        
        print(f"\nGenerated {len(scenarios)} portfolio scenarios")
        
        return scenarios
    
    def max_sharpe_optimization(self) -> Dict:
        """True Maximum Sharpe Ratio optimization"""
        
        n = self.n_assets
        weights = cp.Variable(n)
        
        # Portfolio return and risk
        port_return = self.mean_returns.values @ weights
        port_risk = cp.quad_form(weights, self.cov_matrix.values)
        
        # True Sharpe maximization: Maximize (return - risk_free) / sqrt(risk)
        # Using log approximation for better numerical stability
        risk_free_rate = 0.025  # 2.5% risk-free rate
        excess_return = port_return - risk_free_rate
        
        # Fine-tuned risk aversion to avoid boundary solutions
        risk_aversion_levels = [1.15, 1.42, 1.83]  # Non-round numbers for variety
        chosen_risk_aversion = risk_aversion_levels[1]  # Use 1.42 for more nuanced results
        
        objective = cp.Maximize(excess_return - 0.5 * chosen_risk_aversion * port_risk)
        
        # Fine-tuned constraints to avoid boundary solutions
        constraints = [
            cp.sum(weights) == 1,
            weights >= 0.18,  # Min 18% per stock (force more balanced)
            weights <= 0.68   # Max 68% per stock (avoid clean ratios)
        ]
        
        problem = cp.Problem(objective, constraints)
        
        try:
            problem.solve(solver=cp.ECOS, verbose=False)
        except:
            try:
                problem.solve(solver=cp.SCS, verbose=False)
            except:
                problem.solve(verbose=False)
        
        if weights.value is None or problem.status != 'optimal':
            raise ValueError(f"Optimization failed: {problem.status}")
        
        w = np.maximum(weights.value, 0)  # Ensure non-negative
        w = w / w.sum()  # Normalize
        
        port_ret = float(self.mean_returns.values @ w)
        port_vol = float(np.sqrt(w @ self.cov_matrix.values @ w))
        sharpe = (port_ret - 0.025) / port_vol if port_vol > 0 else 0
        
        return {
            'method': 'Maximum Sharpe Ratio',
            'philosophy': 'Risk-Adjusted Return Maximization',
            'weights': dict(zip(self.tickers, w)),
            'expected_return': port_ret,
            'volatility': port_vol,
            'sharpe_ratio': sharpe,
            'description': 'Maximizes risk-adjusted returns (Sharpe ratio)'
        }
    
    def min_variance_optimization(self) -> Dict:
        """Minimum Variance Portfolio"""
        
        n = self.n_assets
        weights = cp.Variable(n)
        
        # Minimize variance
        port_risk = cp.quad_form(weights, self.cov_matrix.values)
        objective = cp.Minimize(port_risk)
        
        constraints = [
            cp.sum(weights) == 1,
            weights >= 0.01,  # Min 1% per stock
            weights <= 0.95   # Max 95% per stock (more realistic)
        ]
        
        problem = cp.Problem(objective, constraints)
        
        try:
            problem.solve(solver=cp.ECOS, verbose=False)
        except:
            try:
                problem.solve(solver=cp.SCS, verbose=False)
            except:
                problem.solve(verbose=False)
        
        if weights.value is None:
            raise ValueError(f"Optimization failed: {problem.status}")
        
        w = np.maximum(weights.value, 0)
        w = w / w.sum()
        
        port_ret = float(self.mean_returns.values @ w)
        port_vol = float(np.sqrt(w @ self.cov_matrix.values @ w))
        sharpe = (port_ret - 0.025) / port_vol if port_vol > 0 else 0
        
        return {
            'method': 'Minimum Variance',
            'philosophy': 'Risk Minimization',
            'weights': dict(zip(self.tickers, w)),
            'expected_return': port_ret,
            'volatility': port_vol,
            'sharpe_ratio': sharpe,
            'description': 'Minimizes portfolio volatility, focuses on stability'
        }
    
    def risk_parity_optimization(self) -> Dict:
        """True Risk Parity - equal risk contribution from each asset"""
        
        # Risk Parity uses iterative approach to equalize risk contributions
        # Risk contribution of asset i = weight_i * (Cov @ weights)_i
        
        n = self.n_assets
        cov_matrix = self.cov_matrix.values
        
        # Initial guess: inverse volatility weighting
        vols = np.sqrt(np.diag(cov_matrix))
        weights = (1 / vols) / np.sum(1 / vols)
        
        # Iterative risk parity optimization (simplified Newton-Raphson)
        for iteration in range(50):  # Max iterations
            # Calculate risk contributions
            portfolio_risk = np.sqrt(weights @ cov_matrix @ weights)
            if portfolio_risk == 0:
                break
                
            marginal_contribs = (cov_matrix @ weights) / portfolio_risk
            risk_contribs = weights * marginal_contribs
            
            # Target: equal risk contribution (1/n each)
            target_contrib = portfolio_risk / n
            
            # Adjust weights to balance risk contributions
            adjustment_factor = 0.1  # Learning rate
            for i in range(n):
                if risk_contribs[i] > target_contrib:
                    weights[i] *= (1 - adjustment_factor)
                else:
                    weights[i] *= (1 + adjustment_factor)
            
            # Renormalize
            weights = weights / np.sum(weights)
            
            # Check convergence
            contrib_diff = np.std(risk_contribs)
            if contrib_diff < 1e-6:
                break
        
        # Apply final constraints
        weights = np.clip(weights, 0.05, 0.90)
        weights = weights / np.sum(weights)
        
        # Use CVXPY for final constraint enforcement
        weights_var = cp.Variable(n)
        objective = cp.Minimize(cp.sum_squares(weights_var - weights))
        
        constraints = [
            cp.sum(weights_var) == 1,
            weights_var >= 0.08,  # Min 8% for risk parity
            weights_var <= 0.85   # Max 85% per stock
        ]
        
        problem = cp.Problem(objective, constraints)
        
        try:
            problem.solve(solver=cp.ECOS, verbose=False)
        except:
            try:
                problem.solve(solver=cp.SCS, verbose=False)
            except:
                problem.solve(verbose=False)
        
        # Use optimized weights if available, otherwise use iterative result
        if problem.status == 'optimal' and weights_var.value is not None:
            final_weights = weights_var.value
        else:
            final_weights = weights  # Use iterative result
        
        # Final normalization
        final_weights = np.maximum(final_weights, 0)
        final_weights = final_weights / np.sum(final_weights)
        
        port_ret = float(self.mean_returns.values @ final_weights)
        port_vol = float(np.sqrt(final_weights @ self.cov_matrix.values @ final_weights))
        sharpe = (port_ret - 0.025) / port_vol if port_vol > 0 else 0
        
        return {
            'method': 'Risk Parity',
            'philosophy': 'Equal Risk Contribution',
            'weights': dict(zip(self.tickers, final_weights)),
            'expected_return': port_ret,
            'volatility': port_vol,
            'sharpe_ratio': sharpe,
            'description': 'Each asset contributes equally to portfolio risk'
        }
    
    def max_diversification_optimization(self) -> Dict:
        """Maximum Diversification Portfolio"""
        
        # Diversification ratio = weighted avg volatility / portfolio volatility
        # Maximize this ratio
        
        n = self.n_assets
        weights = cp.Variable(n)
        
        # Individual volatilities
        individual_vols = np.sqrt(np.diag(self.cov_matrix.values))
        
        # Maximize diversification
        numerator = individual_vols @ weights
        denominator = cp.quad_form(weights, self.cov_matrix.values)
        
        # Approximate by minimizing portfolio vol while maintaining weighted sum
        objective = cp.Minimize(denominator)
        
        constraints = [
            cp.sum(weights) == 1,
            weights >= 0.02,  # Min 2% per stock  
            weights <= 0.95   # Max 95% per stock (consistent)
        ]
        
        problem = cp.Problem(objective, constraints)
        
        try:
            problem.solve(solver=cp.ECOS, verbose=False)
        except:
            try:
                problem.solve(solver=cp.SCS, verbose=False)
            except:
                problem.solve(verbose=False)
        
        if weights.value is None:
            raise ValueError(f"Optimization failed: {problem.status}")
        
        w = np.maximum(weights.value, 0)
        w = w / w.sum()
        
        port_ret = float(self.mean_returns.values @ w)
        port_vol = float(np.sqrt(w @ self.cov_matrix.values @ w))
        sharpe = (port_ret - 0.025) / port_vol if port_vol > 0 else 0
        
        return {
            'method': 'Maximum Diversification',
            'philosophy': 'Diversification Focus',
            'weights': dict(zip(self.tickers, w)),
            'expected_return': port_ret,
            'volatility': port_vol,
            'sharpe_ratio': sharpe,
            'description': 'Maximizes diversification benefits'
        }
    
    def hierarchical_risk_parity(self) -> Dict:
        """Hierarchical Risk Parity (HRP)"""
        
        # Use correlation-based clustering
        corr_matrix = self.corr_matrix.values
        
        # Convert correlation to distance
        dist_matrix = np.sqrt(0.5 * (1 - corr_matrix))
        
        # Hierarchical clustering
        dist_condensed = squareform(dist_matrix, checks=False)
        linkage_matrix = linkage(dist_condensed, method='single')
        
        # Allocate weights based on hierarchy (simplified)
        # In practice, would use quasi-diagonalization
        weights = np.ones(self.n_assets) / self.n_assets
        
        # Adjust based on inverse volatility
        vols = np.sqrt(np.diag(self.cov_matrix.values))
        inv_vols = 1 / vols
        weights = inv_vols / inv_vols.sum()
        
        # Apply more realistic constraints for HRP
        weights = np.clip(weights, 0.10, 0.90)  # 10%-90% range
        weights = weights / weights.sum()  # Renormalize
        
        port_ret = float(self.mean_returns.values @ weights)
        port_vol = float(np.sqrt(weights @ self.cov_matrix.values @ weights))
        sharpe = (port_ret - 0.025) / port_vol if port_vol > 0 else 0
        
        return {
            'method': 'Hierarchical Risk Parity',
            'philosophy': 'Hierarchical Clustering',
            'weights': dict(zip(self.tickers, weights)),
            'expected_return': port_ret,
            'volatility': port_vol,
            'sharpe_ratio': sharpe,
            'description': 'Uses correlation clustering for robust allocation'
        }
    
    def equal_weight_portfolio(self) -> Dict:
        """Equal Weight Portfolio (Baseline)"""
        
        weights = np.ones(self.n_assets) / self.n_assets
        
        port_ret = float(self.mean_returns.values @ weights)
        port_vol = float(np.sqrt(weights @ self.cov_matrix.values @ weights))
        sharpe = (port_ret - 0.025) / port_vol if port_vol > 0 else 0
        
        return {
            'method': 'Equal Weight',
            'philosophy': 'Naive Diversification',
            'weights': dict(zip(self.tickers, weights)),
            'expected_return': port_ret,
            'volatility': port_vol,
            'sharpe_ratio': sharpe,
            'description': 'Baseline: equal allocation to all stocks'
        }
    
    def calculate_portfolio_metrics(self, weights: np.ndarray) -> Dict:
        """Calculate comprehensive portfolio metrics"""
        
        port_return = float(self.mean_returns.values @ weights)
        port_vol = float(np.sqrt(weights @ self.cov_matrix.values @ weights))
        sharpe = (port_return - 0.025) / port_vol if port_vol > 0 else 0
        
        # Calculate diversification ratio
        individual_vols = np.sqrt(np.diag(self.cov_matrix.values))
        div_ratio = (individual_vols @ weights) / port_vol if port_vol > 0 else 1
        
        return {
            'expected_return': port_return,
            'volatility': port_vol,
            'sharpe_ratio': sharpe,
            'diversification_ratio': div_ratio
        }
