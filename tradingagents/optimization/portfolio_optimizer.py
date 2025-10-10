"""
Enterprise Portfolio Optimization Engine
Advanced portfolio optimization methods for institutional investors
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.covariance import LedoitWolf
import cvxpy as cp
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class EnterprisePortfolioOptimizer:
    """
    Advanced portfolio optimization using multiple sophisticated methods
    """
    
    def __init__(self, returns_data: pd.DataFrame, risk_free_rate: float = 0.02):
        """
        Initialize the optimizer with returns data
        
        Args:
            returns_data: DataFrame with asset returns (assets as columns, dates as rows)
            risk_free_rate: Annual risk-free rate (default 2%)
        """
        self.returns = returns_data
        self.assets = returns_data.columns.tolist()
        self.n_assets = len(self.assets)
        self.risk_free_rate = risk_free_rate
        
        # Calculate statistics
        self.mean_returns = returns_data.mean() * 252  # Annualized
        self.cov_matrix = self._calculate_covariance_matrix()
        
    def _calculate_covariance_matrix(self) -> np.ndarray:
        """Calculate robust covariance matrix using Ledoit-Wolf shrinkage"""
        lw = LedoitWolf()
        cov_matrix, _ = lw.fit(self.returns).covariance_, lw.shrinkage_
        return cov_matrix * 252  # Annualized
    
    def markowitz_optimization(self, target_return: Optional[float] = None, 
                             max_weight: float = 0.4) -> Dict:
        """
        Mean-Variance Optimization (Markowitz)
        
        Args:
            target_return: Target annual return (if None, optimizes for max Sharpe ratio)
            max_weight: Maximum weight per asset
            
        Returns:
            Dictionary with weights, expected return, volatility, and Sharpe ratio
        """
        n = self.n_assets
        
        # Define variables
        weights = cp.Variable(n)
        
        # Expected return and risk
        expected_return = self.mean_returns.values @ weights
        portfolio_risk = cp.quad_form(weights, self.cov_matrix)
        
        # Constraints
        constraints = [
            cp.sum(weights) == 1,  # Fully invested
            weights >= 0,  # Long-only
            weights <= max_weight  # Position limits
        ]
        
        if target_return is not None:
            # Minimize risk for target return
            constraints.append(expected_return >= target_return)
            objective = cp.Minimize(portfolio_risk)
        else:
            # Maximize Sharpe ratio (equivalent to maximizing return/risk)
            objective = cp.Maximize(expected_return - 0.5 * 0.1 * portfolio_risk)
        
        # Solve optimization
        problem = cp.Problem(objective, constraints)
        problem.solve(solver=cp.ECOS)
        
        if weights.value is None:
            raise ValueError("Optimization failed to converge")
        
        # Calculate metrics
        w = weights.value
        port_return = float(self.mean_returns.values @ w)
        port_vol = float(np.sqrt(w @ self.cov_matrix @ w))
        sharpe_ratio = (port_return - self.risk_free_rate) / port_vol
        
        return {
            'method': 'Markowitz (Mean-Variance)',
            'weights': dict(zip(self.assets, w)),
            'expected_return': port_return,
            'volatility': port_vol,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': self._estimate_max_drawdown(w)
        }
    
    def risk_parity_optimization(self) -> Dict:
        """
        Risk Parity Portfolio - Equal risk contribution from each asset
        
        Returns:
            Dictionary with weights and portfolio metrics
        """
        def risk_budget_objective(weights):
            """Objective function for risk parity"""
            weights = np.array(weights)
            portfolio_vol = np.sqrt(weights @ self.cov_matrix @ weights)
            
            # Marginal risk contributions
            marginal_contrib = (self.cov_matrix @ weights) / portfolio_vol
            
            # Risk contributions
            risk_contrib = weights * marginal_contrib
            
            # Target is equal risk contribution (1/n each)
            target_risk = np.ones(self.n_assets) / self.n_assets
            
            # Sum of squared deviations from target
            return np.sum((risk_contrib / np.sum(risk_contrib) - target_risk) ** 2)
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Fully invested
        ]
        
        bounds = [(0.01, 0.4) for _ in range(self.n_assets)]  # Min 1%, max 40%
        
        # Initial guess (equal weights)
        x0 = np.ones(self.n_assets) / self.n_assets
        
        # Optimize
        result = minimize(risk_budget_objective, x0, method='SLSQP', 
                         bounds=bounds, constraints=constraints)
        
        if not result.success:
            raise ValueError("Risk parity optimization failed")
        
        # Calculate metrics
        w = result.x
        port_return = float(self.mean_returns.values @ w)
        port_vol = float(np.sqrt(w @ self.cov_matrix @ w))
        sharpe_ratio = (port_return - self.risk_free_rate) / port_vol
        
        return {
            'method': 'Risk Parity',
            'weights': dict(zip(self.assets, w)),
            'expected_return': port_return,
            'volatility': port_vol,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': self._estimate_max_drawdown(w)
        }
    
    def minimum_variance_optimization(self, max_weight: float = 0.4) -> Dict:
        """
        Minimum Variance Portfolio
        
        Args:
            max_weight: Maximum weight per asset
            
        Returns:
            Dictionary with weights and portfolio metrics
        """
        n = self.n_assets
        
        # Define variables
        weights = cp.Variable(n)
        
        # Objective: minimize portfolio variance
        portfolio_risk = cp.quad_form(weights, self.cov_matrix)
        objective = cp.Minimize(portfolio_risk)
        
        # Constraints
        constraints = [
            cp.sum(weights) == 1,  # Fully invested
            weights >= 0,  # Long-only
            weights <= max_weight  # Position limits
        ]
        
        # Solve optimization
        problem = cp.Problem(objective, constraints)
        problem.solve(solver=cp.ECOS)
        
        if weights.value is None:
            raise ValueError("Minimum variance optimization failed")
        
        # Calculate metrics
        w = weights.value
        port_return = float(self.mean_returns.values @ w)
        port_vol = float(np.sqrt(w @ self.cov_matrix @ w))
        sharpe_ratio = (port_return - self.risk_free_rate) / port_vol
        
        return {
            'method': 'Minimum Variance',
            'weights': dict(zip(self.assets, w)),
            'expected_return': port_return,
            'volatility': port_vol,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': self._estimate_max_drawdown(w)
        }
    
    def cvar_optimization(self, confidence_level: float = 0.95, 
                         max_weight: float = 0.4) -> Dict:
        """
        Conditional Value at Risk (CVaR) Optimization
        
        Args:
            confidence_level: Confidence level for CVaR (default 95%)
            max_weight: Maximum weight per asset
            
        Returns:
            Dictionary with weights and portfolio metrics
        """
        n = self.n_assets
        T = len(self.returns)
        alpha = 1 - confidence_level
        
        # Define variables
        weights = cp.Variable(n)
        var = cp.Variable()  # Value at Risk
        u = cp.Variable(T)   # Auxiliary variables for CVaR
        
        # Portfolio returns for each time period
        portfolio_returns = self.returns.values @ weights
        
        # CVaR constraints
        constraints = [
            cp.sum(weights) == 1,  # Fully invested
            weights >= 0,  # Long-only
            weights <= max_weight,  # Position limits
            u >= 0,  # Auxiliary variables non-negative
            u >= -portfolio_returns - var  # CVaR constraint
        ]
        
        # Objective: minimize CVaR
        cvar = var + (1/alpha) * cp.sum(u) / T
        objective = cp.Minimize(cvar)
        
        # Solve optimization
        problem = cp.Problem(objective, constraints)
        problem.solve(solver=cp.ECOS)
        
        if weights.value is None:
            raise ValueError("CVaR optimization failed")
        
        # Calculate metrics
        w = weights.value
        port_return = float(self.mean_returns.values @ w)
        port_vol = float(np.sqrt(w @ self.cov_matrix @ w))
        sharpe_ratio = (port_return - self.risk_free_rate) / port_vol
        
        return {
            'method': f'CVaR Optimization ({confidence_level*100}%)',
            'weights': dict(zip(self.assets, w)),
            'expected_return': port_return,
            'volatility': port_vol,
            'sharpe_ratio': sharpe_ratio,
            'cvar': float(cvar.value),
            'max_drawdown': self._estimate_max_drawdown(w)
        }
    
    def hierarchical_risk_parity(self) -> Dict:
        """
        Hierarchical Risk Parity (HRP) using machine learning clustering
        
        Returns:
            Dictionary with weights and portfolio metrics
        """
        from scipy.cluster.hierarchy import linkage, dendrogram, cut_tree
        from scipy.spatial.distance import squareform
        
        # Calculate distance matrix from correlation
        corr_matrix = self.returns.corr()
        distance_matrix = np.sqrt(0.5 * (1 - corr_matrix))
        
        # Hierarchical clustering
        condensed_distances = squareform(distance_matrix, checks=False)
        linkage_matrix = linkage(condensed_distances, method='ward')
        
        # Get cluster tree
        def get_cluster_var(cluster_items):
            """Calculate cluster variance"""
            if len(cluster_items) == 1:
                return self.cov_matrix[cluster_items[0], cluster_items[0]]
            cluster_cov = self.cov_matrix[np.ix_(cluster_items, cluster_items)]
            ivp = 1.0 / np.diag(cluster_cov)  # Inverse variance weights
            ivp = ivp / ivp.sum()
            return np.dot(ivp, np.dot(cluster_cov, ivp))
        
        def get_rec_bipart(linkage_matrix, sort_ix):
            """Recursively bisect the dendrogram"""
            weights = pd.Series(1.0, index=sort_ix)
            cluster_items = [sort_ix]
            
            while len(cluster_items) > 0:
                cluster_items = [
                    i[j:k] for i in cluster_items
                    for j, k in ((0, len(i) // 2), (len(i) // 2, len(i)))
                    if len(i) > 1
                ]
                
                for i in range(0, len(cluster_items), 2):
                    cluster0 = cluster_items[i]
                    cluster1 = cluster_items[i + 1]
                    
                    # Calculate cluster variances
                    var0 = get_cluster_var(cluster0)
                    var1 = get_cluster_var(cluster1)
                    
                    # Allocate weight inversely to variance
                    alpha = 1 - var0 / (var0 + var1)
                    weights[cluster0] *= alpha
                    weights[cluster1] *= 1 - alpha
            
            return weights
        
        # Sort assets by hierarchical clustering
        sort_ix = np.arange(self.n_assets)
        
        # Get HRP weights
        hrp_weights = get_rec_bipart(linkage_matrix, sort_ix)
        w = hrp_weights.values
        
        # Calculate metrics
        port_return = float(self.mean_returns.values @ w)
        port_vol = float(np.sqrt(w @ self.cov_matrix @ w))
        sharpe_ratio = (port_return - self.risk_free_rate) / port_vol
        
        return {
            'method': 'Hierarchical Risk Parity (HRP)',
            'weights': dict(zip(self.assets, w)),
            'expected_return': port_return,
            'volatility': port_vol,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': self._estimate_max_drawdown(w)
        }
    
    def black_litterman_optimization(self, investor_views: Dict = None, 
                                   confidence: List[float] = None) -> Dict:
        """
        Black-Litterman Model with investor views
        
        Args:
            investor_views: Dictionary with asset views {'AAPL': 0.12, 'MSFT': 0.08}
            confidence: List of confidence levels for each view (0-1)
            
        Returns:
            Dictionary with weights and portfolio metrics
        """
        # Market capitalization weights (proxy for equilibrium)
        market_caps = np.ones(self.n_assets) / self.n_assets  # Equal for simplicity
        
        # Risk aversion parameter
        risk_aversion = (self.mean_returns @ market_caps - self.risk_free_rate) / \
                       (market_caps @ self.cov_matrix @ market_caps)
        
        # Equilibrium returns
        pi = risk_aversion * self.cov_matrix @ market_caps
        
        if investor_views is None:
            # No views, return market portfolio
            mu_bl = pi
        else:
            # Incorporate investor views
            k = len(investor_views)
            P = np.zeros((k, self.n_assets))  # Picking matrix
            Q = np.zeros(k)  # View returns
            
            for i, (asset, view_return) in enumerate(investor_views.items()):
                if asset in self.assets:
                    asset_idx = self.assets.index(asset)
                    P[i, asset_idx] = 1
                    Q[i] = view_return
            
            # Uncertainty matrix
            if confidence is None:
                confidence = [0.5] * k  # Medium confidence
            
            omega = np.diag([(1/conf - 1) * (P[i:i+1] @ self.cov_matrix @ P[i:i+1].T)[0,0] 
                           for i, conf in enumerate(confidence)])
            
            # Black-Litterman formula
            tau = 0.025  # Scaling factor
            M1 = np.linalg.inv(tau * self.cov_matrix)
            M2 = P.T @ np.linalg.inv(omega) @ P
            M3 = np.linalg.inv(tau * self.cov_matrix) @ pi
            M4 = P.T @ np.linalg.inv(omega) @ Q
            
            mu_bl = np.linalg.solve(M1 + M2, M3 + M4)
        
        # Optimize with Black-Litterman returns
        n = self.n_assets
        weights = cp.Variable(n)
        
        # Expected return and risk with BL estimates
        expected_return = mu_bl @ weights
        portfolio_risk = cp.quad_form(weights, self.cov_matrix)
        
        # Objective: maximize utility (return - risk penalty)
        objective = cp.Maximize(expected_return - 0.5 * risk_aversion * portfolio_risk)
        
        # Constraints
        constraints = [
            cp.sum(weights) == 1,  # Fully invested
            weights >= 0,  # Long-only
            weights <= 0.4  # Position limits
        ]
        
        # Solve optimization
        problem = cp.Problem(objective, constraints)
        problem.solve(solver=cp.ECOS)
        
        if weights.value is None:
            raise ValueError("Black-Litterman optimization failed")
        
        # Calculate metrics
        w = weights.value
        port_return = float(self.mean_returns.values @ w)
        port_vol = float(np.sqrt(w @ self.cov_matrix @ w))
        sharpe_ratio = (port_return - self.risk_free_rate) / port_vol
        
        return {
            'method': 'Black-Litterman',
            'weights': dict(zip(self.assets, w)),
            'expected_return': port_return,
            'volatility': port_vol,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': self._estimate_max_drawdown(w)
        }
    
    def _estimate_max_drawdown(self, weights: np.ndarray) -> float:
        """Estimate maximum drawdown for given weights"""
        portfolio_returns = (self.returns.values @ weights)
        cumulative = np.cumprod(1 + portfolio_returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        return float(np.min(drawdown))
    
    def optimize_portfolio(self, strategy: str = "markowitz", **kwargs) -> Dict:
        """
        Main optimization method - calls specific optimizer based on strategy
        
        Args:
            strategy: Optimization strategy name
            **kwargs: Additional arguments for specific optimizers
            
        Returns:
            Optimization results dictionary
        """
        strategies = {
            "markowitz": self.markowitz_optimization,
            "risk_parity": self.risk_parity_optimization,
            "minimum_variance": self.minimum_variance_optimization,
            "cvar": self.cvar_optimization,
            "hrp": self.hierarchical_risk_parity,
            "black_litterman": self.black_litterman_optimization
        }
        
        if strategy not in strategies:
            raise ValueError(f"Unknown strategy: {strategy}. Available: {list(strategies.keys())}")
        
        return strategies[strategy](**kwargs)
    
    def compare_strategies(self, strategies: List[str] = None) -> pd.DataFrame:
        """
        Compare multiple optimization strategies
        
        Args:
            strategies: List of strategy names to compare
            
        Returns:
            DataFrame comparing strategy performance
        """
        if strategies is None:
            strategies = ["markowitz", "risk_parity", "minimum_variance", "cvar", "hrp"]
        
        results = []
        for strategy in strategies:
            try:
                result = self.optimize_portfolio(strategy)
                results.append({
                    'Strategy': result['method'],
                    'Expected Return': f"{result['expected_return']:.2%}",
                    'Volatility': f"{result['volatility']:.2%}",
                    'Sharpe Ratio': f"{result['sharpe_ratio']:.3f}",
                    'Max Drawdown': f"{result['max_drawdown']:.2%}"
                })
            except Exception as e:
                print(f"Strategy {strategy} failed: {e}")
        
        return pd.DataFrame(results)
