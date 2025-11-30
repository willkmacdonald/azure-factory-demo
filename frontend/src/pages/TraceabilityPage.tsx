import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Package,
  Truck,
  ShoppingCart,
  CheckCircle,
  AlertTriangle,
  ArrowRight,
  Loader2,
  AlertCircle,
  Info,
  ChevronDown,
  Search,
} from 'lucide-react';
import { apiService, getErrorMessage } from '../api/client';
import type {
  StatsResponse,
  ProductionBatch,
  Supplier,
  BackwardTrace,
  SupplierImpact,
  Order,
  OrderBatches,
  QualityIssue,
} from '../types/api';

/**
 * TraceabilityPage Component
 *
 * Provides supply chain traceability features with three main views:
 * 1. Batch Lookup - Trace materials and suppliers used in a production batch
 * 2. Supplier Impact - Analyze supplier quality impact on production
 * 3. Order Status - Track order fulfillment status and quality
 */
const TraceabilityPage: React.FC = () => {
  // Tab state
  const [currentTab, setCurrentTab] = useState<number>(0);

  // Common states
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Tab 1: Batch Lookup states
  const [batches, setBatches] = useState<ProductionBatch[]>([]);
  const [selectedBatch, setSelectedBatch] = useState<ProductionBatch | null>(null);
  const [backwardTrace, setBackwardTrace] = useState<BackwardTrace | null>(null);
  const [batchLoading, setBatchLoading] = useState<boolean>(false);
  const [batchSearchQuery, setBatchSearchQuery] = useState<string>('');
  const [showBatchDropdown, setShowBatchDropdown] = useState<boolean>(false);

  // Tab 2: Supplier Impact states
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [selectedSupplierId, setSelectedSupplierId] = useState<string>('');
  const [supplierImpact, setSupplierImpact] = useState<SupplierImpact | null>(null);
  const [supplierLoading, setSupplierLoading] = useState<boolean>(false);

  // Tab 3: Order Status states
  const [orders, setOrders] = useState<Order[]>([]);
  const [orderStatusFilter, setOrderStatusFilter] = useState<string>('all');
  const [filteredOrders, setFilteredOrders] = useState<Order[]>([]);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [orderBatches, setOrderBatches] = useState<OrderBatches | null>(null);
  const [orderLoading, setOrderLoading] = useState<boolean>(false);

  // Fetch initial data on mount
  useEffect(() => {
    const fetchInitialData = async (): Promise<void> => {
      try {
        setLoading(true);
        setError(null);

        // Fetch stats
        const statsResponse = await apiService.getStats();
        setStats(statsResponse);

        if (statsResponse.exists) {
          // Fetch data for all tabs in parallel
          const [batchesRes, suppliersRes, ordersRes] = await Promise.all([
            apiService.listBatches({ limit: 100 }),
            apiService.listSuppliers(),
            apiService.listOrders({ limit: 100 }),
          ]);

          setBatches(batchesRes);
          setSuppliers(suppliersRes);
          setOrders(ordersRes);
          setFilteredOrders(ordersRes);
        }
      } catch (err) {
        setError(getErrorMessage(err));
        console.error('Failed to fetch traceability data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchInitialData();
  }, []);

  // ========================================
  // Tab 1: Batch Lookup Handlers
  // ========================================

  const handleBatchSelect = async (batch: ProductionBatch): Promise<void> => {
    setSelectedBatch(batch);
    setBackwardTrace(null);
    setShowBatchDropdown(false);
    setBatchSearchQuery(`${batch.batch_id} - ${batch.part_number}`);

    try {
      setBatchLoading(true);
      const trace = await apiService.getBackwardTrace(batch.batch_id);
      setBackwardTrace(trace);
    } catch (err) {
      console.error('Failed to fetch backward trace:', err);
      setError(getErrorMessage(err));
    } finally {
      setBatchLoading(false);
    }
  };

  const filteredBatches = batches.filter((batch) =>
    `${batch.batch_id} ${batch.part_number}`.toLowerCase().includes(batchSearchQuery.toLowerCase())
  );

  // ========================================
  // Tab 2: Supplier Impact Handlers
  // ========================================

  const handleSupplierChange = async (event: React.ChangeEvent<HTMLSelectElement>): Promise<void> => {
    const supplierId = event.target.value;
    setSelectedSupplierId(supplierId);
    setSupplierImpact(null);

    if (supplierId) {
      try {
        setSupplierLoading(true);
        const impact = await apiService.getSupplierImpact(supplierId);
        setSupplierImpact(impact);
      } catch (err) {
        console.error('Failed to fetch supplier impact:', err);
        setError(getErrorMessage(err));
      } finally {
        setSupplierLoading(false);
      }
    }
  };

  // ========================================
  // Tab 3: Order Status Handlers
  // ========================================

  // Filter orders when status filter changes
  useEffect(() => {
    if (orderStatusFilter === 'all') {
      setFilteredOrders(orders);
    } else {
      setFilteredOrders(orders.filter((order) => order.status === orderStatusFilter));
    }
  }, [orderStatusFilter, orders]);

  const handleOrderStatusFilterChange = (event: React.ChangeEvent<HTMLSelectElement>): void => {
    setOrderStatusFilter(event.target.value);
  };

  const handleOrderSelect = async (order: Order): Promise<void> => {
    setSelectedOrder(order);
    setOrderBatches(null);

    try {
      setOrderLoading(true);
      const batches = await apiService.getOrderBatches(order.id);
      setOrderBatches(batches);
    } catch (err) {
      console.error('Failed to fetch order batches:', err);
      setError(getErrorMessage(err));
    } finally {
      setOrderLoading(false);
    }
  };

  // ========================================
  // Helper Functions
  // ========================================

  const getOrderStatusStyles = (status: string): string => {
    switch (status) {
      case 'Completed':
      case 'Shipped':
        return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 border-green-200 dark:border-green-800';
      case 'InProgress':
        return 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 border-blue-200 dark:border-blue-800';
      case 'Delayed':
        return 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 border-red-200 dark:border-red-800';
      case 'Pending':
        return 'bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-300 border-amber-200 dark:border-amber-800';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300 border-gray-200 dark:border-gray-600';
    }
  };

  const getSupplierStatusStyles = (status: string): string => {
    switch (status) {
      case 'Active':
        return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 border-green-200 dark:border-green-800';
      case 'OnHold':
        return 'bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-300 border-amber-200 dark:border-amber-800';
      case 'Suspended':
        return 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 border-red-200 dark:border-red-800';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300 border-gray-200 dark:border-gray-600';
    }
  };

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  // Tab configuration
  const tabs = [
    { icon: Package, label: 'Batch Lookup' },
    { icon: Truck, label: 'Supplier Impact' },
    { icon: ShoppingCart, label: 'Order Status' },
  ];

  // ========================================
  // Render Functions
  // ========================================

  // Loading state
  if (loading) {
    return (
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-center items-center min-h-[400px]">
            <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !stats?.exists) {
    return (
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mt-8">
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-red-800 dark:text-red-200">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // No data state
  if (!stats?.exists) {
    return (
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Supply Chain Traceability
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Track materials, suppliers, and orders throughout the production lifecycle
            </p>
          </div>
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 flex items-start gap-3">
            <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
            <p className="text-blue-800 dark:text-blue-200">
              No production data available. Please generate data using the setup endpoint.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Supply Chain Traceability
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Track materials, suppliers, and orders throughout the production lifecycle
          </p>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 dark:border-gray-700 mb-6">
          <nav className="flex gap-1" role="tablist">
            {tabs.map((tab, index) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.label}
                  role="tab"
                  aria-selected={currentTab === index}
                  onClick={() => setCurrentTab(index)}
                  className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                    currentTab === index
                      ? 'border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400'
                      : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Tab 1: Batch Lookup */}
        {currentTab === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                Backward Traceability - Batch to Suppliers
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
                Select a production batch to trace materials back to their suppliers
              </p>

              {/* Batch Autocomplete */}
              <div className="relative mb-6">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search production batches..."
                    value={batchSearchQuery}
                    onChange={(e) => {
                      setBatchSearchQuery(e.target.value);
                      setShowBatchDropdown(true);
                    }}
                    onFocus={() => setShowBatchDropdown(true)}
                    className="w-full pl-10 pr-4 py-2.5 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <AnimatePresence>
                  {showBatchDropdown && filteredBatches.length > 0 && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg max-h-60 overflow-y-auto"
                    >
                      {filteredBatches.slice(0, 10).map((batch) => (
                        <button
                          key={batch.batch_id}
                          onClick={() => handleBatchSelect(batch)}
                          className="w-full px-4 py-2.5 text-left hover:bg-gray-50 dark:hover:bg-gray-600 text-sm text-gray-900 dark:text-white border-b border-gray-100 dark:border-gray-600 last:border-b-0"
                        >
                          <span className="font-medium">{batch.batch_id}</span>
                          <span className="text-gray-500 dark:text-gray-400"> - {batch.part_number}</span>
                          <span className="text-gray-400 dark:text-gray-500 text-xs ml-2">({formatDate(batch.date)})</span>
                        </button>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Loading */}
              {batchLoading && (
                <div className="flex justify-center py-8">
                  <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
                </div>
              )}

              {/* Backward Trace Results */}
              {backwardTrace && !batchLoading && (
                <div>
                  <hr className="border-gray-200 dark:border-gray-700 my-6" />

                  {/* Batch Information */}
                  <h3 className="text-md font-semibold text-gray-900 dark:text-white mb-4">
                    Batch Information
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Batch ID</p>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">{backwardTrace.batch.batch_id}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Machine</p>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">{backwardTrace.batch.machine_name}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Date</p>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">{formatDate(backwardTrace.batch.date)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Production</p>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {backwardTrace.batch.parts_produced} parts ({backwardTrace.batch.good_parts} good, {backwardTrace.batch.scrap_parts} scrap)
                      </p>
                    </div>
                  </div>

                  {/* Materials Used */}
                  <h3 className="text-md font-semibold text-gray-900 dark:text-white mb-4 mt-6">
                    Materials Used ({backwardTrace.materials_trace.length})
                  </h3>
                  <div className="overflow-x-auto bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 mb-6">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                      <thead className="bg-gray-50 dark:bg-gray-900/50">
                        <tr>
                          <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Material</th>
                          <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Lot Number</th>
                          <th scope="col" className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Quantity</th>
                          <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Supplier</th>
                          <th scope="col" className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                        {backwardTrace.materials_trace.map((material, index) => {
                          const linkedIssues = (backwardTrace.batch.quality_issues || []).filter(
                            (issue: QualityIssue) => issue.lot_number === material.lot_number
                          );
                          const hasQualityIssues = linkedIssues.length > 0;

                          return (
                            <tr
                              key={index}
                              className={hasQualityIssues ? 'bg-red-50 dark:bg-red-900/20' : ''}
                            >
                              <td className="px-4 py-3 whitespace-nowrap">
                                <div className="flex items-center gap-2">
                                  {hasQualityIssues && <AlertTriangle className="w-4 h-4 text-red-500" />}
                                  <span className="text-sm text-gray-900 dark:text-gray-100">{material.material_name}</span>
                                </div>
                              </td>
                              <td className="px-4 py-3 whitespace-nowrap">
                                <span className="text-sm font-mono text-gray-900 dark:text-gray-100">{material.lot_number}</span>
                              </td>
                              <td className="px-4 py-3 whitespace-nowrap text-right text-sm text-gray-900 dark:text-gray-100">
                                {material.quantity_used} {material.unit}
                              </td>
                              <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                                {material.supplier?.name || 'Unknown'}
                              </td>
                              <td className="px-4 py-3 whitespace-nowrap text-center">
                                {hasQualityIssues ? (
                                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 border border-red-200 dark:border-red-800">
                                    <AlertTriangle className="w-3 h-3" />
                                    {linkedIssues.length} issue{linkedIssues.length > 1 ? 's' : ''}
                                  </span>
                                ) : (
                                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 border border-green-200 dark:border-green-800">
                                    <CheckCircle className="w-3 h-3" />
                                    OK
                                  </span>
                                )}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>

                  {/* Suppliers Involved */}
                  <h3 className="text-md font-semibold text-gray-900 dark:text-white mb-4">
                    Suppliers Involved ({backwardTrace.suppliers.length})
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {backwardTrace.suppliers.map((supplier) => (
                      <div key={supplier.id} className="bg-gray-50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-3">
                          <div>
                            <h4 className="font-semibold text-gray-900 dark:text-white">{supplier.name}</h4>
                            <p className="text-xs text-gray-500 dark:text-gray-400">{supplier.id} - {supplier.type}</p>
                          </div>
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${getSupplierStatusStyles(supplier.status)}`}>
                            {supplier.status}
                          </span>
                        </div>
                        <hr className="border-gray-200 dark:border-gray-600 my-3" />
                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <p className="text-xs text-gray-500 dark:text-gray-400">Quality Rating</p>
                            <p className="text-sm font-medium text-gray-900 dark:text-white">
                              {supplier.quality_metrics.quality_rating?.toFixed(1) || 'N/A'}%
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-500 dark:text-gray-400">Defect Rate</p>
                            <p className="text-sm font-medium text-gray-900 dark:text-white">
                              {supplier.quality_metrics.defect_rate?.toFixed(2) || 'N/A'}%
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {selectedBatch && !backwardTrace && !batchLoading && (
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 flex items-start gap-3">
                  <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                  <p className="text-blue-800 dark:text-blue-200">No traceability data found for this batch</p>
                </div>
              )}
            </div>
          </motion.div>
        )}

        {/* Tab 2: Supplier Impact */}
        {currentTab === 1 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                Supplier Quality Impact Analysis
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
                Analyze how supplier quality affects production batches and orders
              </p>

              {/* Supplier Select */}
              <div className="mb-6">
                <label htmlFor="supplier-select" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Select Supplier
                </label>
                <div className="relative">
                  <select
                    id="supplier-select"
                    value={selectedSupplierId}
                    onChange={handleSupplierChange}
                    className="w-full appearance-none px-4 py-2.5 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 pr-10"
                  >
                    <option value="">Select a supplier...</option>
                    {suppliers.map((supplier) => (
                      <option key={supplier.id} value={supplier.id}>
                        {supplier.name} ({supplier.id}) - Quality: {supplier.quality_metrics.quality_rating?.toFixed(1)}%
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                </div>
              </div>

              {/* Loading */}
              {supplierLoading && (
                <div className="flex justify-center py-8">
                  <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
                </div>
              )}

              {/* Supplier Impact Results */}
              {supplierImpact && !supplierLoading && (
                <div>
                  <hr className="border-gray-200 dark:border-gray-700 my-6" />

                  {/* Summary Cards */}
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                    <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 text-center">
                      <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">{supplierImpact.material_lots_supplied}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Material Lots Supplied</p>
                    </div>
                    <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 text-center">
                      <p className="text-3xl font-bold text-cyan-600 dark:text-cyan-400">{supplierImpact.affected_batches_count}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Batches Affected</p>
                    </div>
                    <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 text-center">
                      <p className="text-3xl font-bold text-amber-600 dark:text-amber-400">{supplierImpact.quality_issues_count}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Quality Issues</p>
                    </div>
                    <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 text-center">
                      <p className="text-3xl font-bold text-red-600 dark:text-red-400">{formatCurrency(supplierImpact.estimated_cost_impact)}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Est. Cost Impact</p>
                    </div>
                  </div>

                  {/* Supplier Details Card */}
                  <div className="bg-gray-50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 rounded-lg p-4 mb-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white">{supplierImpact.supplier.name}</h4>
                        <p className="text-xs text-gray-500 dark:text-gray-400">{supplierImpact.supplier.id} - {supplierImpact.supplier.type}</p>
                      </div>
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${getSupplierStatusStyles(supplierImpact.supplier.status)}`}>
                        {supplierImpact.supplier.status}
                      </span>
                    </div>
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Quality Rating</p>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {supplierImpact.supplier.quality_metrics.quality_rating?.toFixed(1)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">On-Time Delivery</p>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {supplierImpact.supplier.quality_metrics.on_time_delivery_rate?.toFixed(1)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Defect Rate</p>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {supplierImpact.supplier.quality_metrics.defect_rate?.toFixed(2)}%
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Affected Batches */}
                  {supplierImpact.affected_batches.length > 0 && (
                    <>
                      <h3 className="text-md font-semibold text-gray-900 dark:text-white mb-4 mt-6">
                        Affected Production Batches ({supplierImpact.affected_batches.length})
                      </h3>
                      <div className="overflow-x-auto bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 mb-6">
                        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                          <thead className="bg-gray-50 dark:bg-gray-900/50">
                            <tr>
                              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Batch ID</th>
                              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Date</th>
                              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Machine</th>
                              <th scope="col" className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Parts</th>
                              <th scope="col" className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Scrap</th>
                              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Materials</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                            {supplierImpact.affected_batches.map((batch) => (
                              <tr key={batch.batch_id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                                <td className="px-4 py-3 whitespace-nowrap">
                                  <span className="text-xs font-mono text-gray-900 dark:text-gray-100">{batch.batch_id}</span>
                                </td>
                                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                                  {formatDate(batch.date)}
                                </td>
                                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                                  {batch.machine_name}
                                </td>
                                <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900 dark:text-gray-100">
                                  {batch.parts_produced}
                                </td>
                                <td className="px-4 py-3 whitespace-nowrap text-right">
                                  {batch.scrap_parts > 0 ? (
                                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300">
                                      {batch.scrap_parts}
                                    </span>
                                  ) : (
                                    <span className="text-sm text-gray-900 dark:text-gray-100">{batch.scrap_parts}</span>
                                  )}
                                </td>
                                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                                  {batch.materials_consumed.length} materials
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </>
                  )}

                  {/* Quality Issues */}
                  {supplierImpact.quality_issues.length > 0 && (
                    <>
                      <h3 className="text-md font-semibold text-gray-900 dark:text-white mb-4 mt-6">
                        Quality Issues ({supplierImpact.quality_issues.length})
                      </h3>
                      <div className="overflow-x-auto bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                          <thead className="bg-gray-50 dark:bg-gray-900/50">
                            <tr>
                              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Batch ID</th>
                              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Date</th>
                              <th scope="col" className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Defects</th>
                              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Types</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                            {supplierImpact.quality_issues.map((issue, index) => (
                              <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                                <td className="px-4 py-3 whitespace-nowrap">
                                  <span className="text-xs font-mono text-gray-900 dark:text-gray-100">{issue.batch_id}</span>
                                </td>
                                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                                  {formatDate(issue.date)}
                                </td>
                                <td className="px-4 py-3 whitespace-nowrap text-right">
                                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300">
                                    {issue.defect_count}
                                  </span>
                                </td>
                                <td className="px-4 py-3">
                                  <div className="flex flex-wrap gap-1">
                                    {issue.defect_types.map((type, idx) => (
                                      <span key={idx} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300 border border-gray-200 dark:border-gray-600">
                                        {type}
                                      </span>
                                    ))}
                                  </div>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </>
                  )}
                </div>
              )}

              {selectedSupplierId && !supplierImpact && !supplierLoading && (
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 flex items-start gap-3">
                  <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                  <p className="text-blue-800 dark:text-blue-200">No impact data found for this supplier</p>
                </div>
              )}
            </div>
          </motion.div>
        )}

        {/* Tab 3: Order Status */}
        {currentTab === 2 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                Order Fulfillment Status
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
                Track customer orders and their production status
              </p>

              {/* Status Filter */}
              <div className="mb-6">
                <label htmlFor="order-status-filter" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Filter by Status
                </label>
                <div className="relative inline-block">
                  <select
                    id="order-status-filter"
                    value={orderStatusFilter}
                    onChange={handleOrderStatusFilterChange}
                    className="appearance-none px-4 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 pr-10"
                  >
                    <option value="all">All Statuses</option>
                    <option value="Pending">Pending</option>
                    <option value="InProgress">In Progress</option>
                    <option value="Completed">Completed</option>
                    <option value="Shipped">Shipped</option>
                    <option value="Delayed">Delayed</option>
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                </div>
              </div>

              {/* Summary Cards */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 text-center">
                  <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">{filteredOrders.length}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {orderStatusFilter === 'all' ? 'Total Orders' : `${orderStatusFilter} Orders`}
                  </p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 text-center">
                  <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                    {orders.filter((o) => o.status === 'Completed' || o.status === 'Shipped').length}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Completed/Shipped</p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 text-center">
                  <p className="text-3xl font-bold text-cyan-600 dark:text-cyan-400">
                    {orders.filter((o) => o.status === 'InProgress').length}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">In Progress</p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 text-center">
                  <p className="text-3xl font-bold text-red-600 dark:text-red-400">
                    {orders.filter((o) => o.status === 'Delayed').length}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Delayed</p>
                </div>
              </div>

              {/* Orders Table */}
              <div className="overflow-x-auto bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-900/50">
                    <tr>
                      <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Order #</th>
                      <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Customer</th>
                      <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Status</th>
                      <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Priority</th>
                      <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Due Date</th>
                      <th scope="col" className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Value</th>
                      <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                    {filteredOrders.length === 0 ? (
                      <tr>
                        <td colSpan={7} className="px-4 py-8 text-center">
                          <p className="text-gray-500 dark:text-gray-400">No orders found</p>
                        </td>
                      </tr>
                    ) : (
                      filteredOrders.map((order) => (
                        <tr
                          key={order.id}
                          onClick={() => handleOrderSelect(order)}
                          className="hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors"
                        >
                          <td className="px-4 py-3 whitespace-nowrap">
                            <span className="text-sm font-mono text-gray-900 dark:text-gray-100">{order.order_number}</span>
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                            {order.customer}
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap">
                            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${getOrderStatusStyles(order.status)}`}>
                              {order.status}
                            </span>
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap">
                            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${
                              order.priority === 'Urgent'
                                ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 border-red-200 dark:border-red-800'
                                : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300 border-gray-200 dark:border-gray-600'
                            }`}>
                              {order.priority}
                            </span>
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                            {formatDate(order.due_date)}
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900 dark:text-gray-100">
                            {formatCurrency(order.total_value)}
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleOrderSelect(order);
                              }}
                              className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded transition-colors"
                            >
                              <ArrowRight className="w-3 h-3" />
                              Details
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>

              {/* Selected Order Details */}
              <AnimatePresence>
                {selectedOrder && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-6"
                  >
                    <hr className="border-gray-200 dark:border-gray-700 mb-6" />
                    <h3 className="text-md font-semibold text-gray-900 dark:text-white mb-4">
                      Order Details - {selectedOrder.order_number}
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Customer</p>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">{selectedOrder.customer}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Status</p>
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${getOrderStatusStyles(selectedOrder.status)}`}>
                          {selectedOrder.status}
                        </span>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Due Date</p>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">{formatDate(selectedOrder.due_date)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Total Value</p>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">{formatCurrency(selectedOrder.total_value)}</p>
                      </div>
                    </div>

                    {/* Order Items */}
                    <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 mt-6">
                      Order Items ({selectedOrder.items.length})
                    </h4>
                    <div className="overflow-x-auto bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 mb-6">
                      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead className="bg-gray-50 dark:bg-gray-900/50">
                          <tr>
                            <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Part Number</th>
                            <th scope="col" className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Quantity</th>
                            <th scope="col" className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Unit Price</th>
                            <th scope="col" className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Total</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                          {selectedOrder.items.map((item, index) => (
                            <tr key={index}>
                              <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{item.part_number}</td>
                              <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900 dark:text-gray-100">{item.quantity}</td>
                              <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900 dark:text-gray-100">{formatCurrency(item.unit_price)}</td>
                              <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900 dark:text-gray-100">{formatCurrency(item.quantity * item.unit_price)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    {/* Production Batches Loading */}
                    {orderLoading && (
                      <div className="flex justify-center py-8">
                        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
                      </div>
                    )}

                    {/* Production Batches */}
                    {orderBatches && !orderLoading && (
                      <>
                        <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 mt-6">
                          Production Batches ({orderBatches.assigned_batches.length})
                        </h4>
                        {orderBatches.assigned_batches.length > 0 ? (
                          <div className="overflow-x-auto bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 mb-6">
                            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                              <thead className="bg-gray-50 dark:bg-gray-900/50">
                                <tr>
                                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Batch ID</th>
                                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Date</th>
                                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Machine</th>
                                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Part</th>
                                  <th scope="col" className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Produced</th>
                                  <th scope="col" className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Good</th>
                                  <th scope="col" className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Scrap</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                                {orderBatches.assigned_batches.map((batch) => (
                                  <tr key={batch.batch_id}>
                                    <td className="px-4 py-3 whitespace-nowrap">
                                      <span className="text-xs font-mono text-gray-900 dark:text-gray-100">{batch.batch_id}</span>
                                    </td>
                                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{formatDate(batch.date)}</td>
                                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{batch.machine_name}</td>
                                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{batch.part_number}</td>
                                    <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900 dark:text-gray-100">{batch.parts_produced}</td>
                                    <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900 dark:text-gray-100">{batch.good_parts}</td>
                                    <td className="px-4 py-3 whitespace-nowrap text-right">
                                      {batch.scrap_parts > 0 ? (
                                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300">
                                          {batch.scrap_parts}
                                        </span>
                                      ) : (
                                        <span className="text-sm text-gray-900 dark:text-gray-100">{batch.scrap_parts}</span>
                                      )}
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        ) : (
                          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 flex items-start gap-3 mb-6">
                            <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                            <p className="text-blue-800 dark:text-blue-200">No production batches assigned to this order yet</p>
                          </div>
                        )}

                        {/* Production Summary */}
                        <div className="bg-gray-50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                          <h5 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">Production Summary</h5>
                          <div className="grid grid-cols-3 gap-4">
                            <div>
                              <p className="text-xs text-gray-500 dark:text-gray-400">Total Produced</p>
                              <p className="text-lg font-bold text-gray-900 dark:text-white">{orderBatches.production_summary.total_produced}</p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500 dark:text-gray-400">Good Parts</p>
                              <p className="text-lg font-bold text-green-600 dark:text-green-400">{orderBatches.production_summary.total_good_parts}</p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500 dark:text-gray-400">Scrap Parts</p>
                              <p className="text-lg font-bold text-red-600 dark:text-red-400">{orderBatches.production_summary.total_scrap}</p>
                            </div>
                          </div>
                        </div>
                      </>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default TraceabilityPage;
