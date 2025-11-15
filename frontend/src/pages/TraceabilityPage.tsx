import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  TextField,
  Autocomplete,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Stack,
  Divider,
  List,
  ListItem,
  ListItemText,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  type SelectChangeEvent,
} from '@mui/material';
import {
  Inventory as InventoryIcon,
  LocalShipping as SupplierIcon,
  ShoppingCart as OrderIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  ArrowForward as ArrowForwardIcon,
} from '@mui/icons-material';
import { apiService, getErrorMessage } from '../api/client';
import type {
  StatsResponse,
  ProductionBatch,
  Supplier,
  BackwardTrace,
  ForwardTrace,
  SupplierImpact,
  Order,
  OrderBatches,
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

  // Handle tab change
  const handleTabChange = (_event: React.SyntheticEvent, newValue: number): void => {
    setCurrentTab(newValue);
  };

  // ========================================
  // Tab 1: Batch Lookup Handlers
  // ========================================

  const handleBatchSelect = async (_event: React.SyntheticEvent, value: ProductionBatch | null): Promise<void> => {
    setSelectedBatch(value);
    setBackwardTrace(null);

    if (value) {
      try {
        setBatchLoading(true);
        const trace = await apiService.getBackwardTrace(value.batch_id);
        setBackwardTrace(trace);
      } catch (err) {
        console.error('Failed to fetch backward trace:', err);
        setError(getErrorMessage(err));
      } finally {
        setBatchLoading(false);
      }
    }
  };

  // ========================================
  // Tab 2: Supplier Impact Handlers
  // ========================================

  const handleSupplierChange = async (event: SelectChangeEvent<string>): Promise<void> => {
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

  const handleOrderStatusFilterChange = (event: SelectChangeEvent<string>): void => {
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

  const getOrderStatusColor = (status: string): 'success' | 'warning' | 'error' | 'info' | 'default' => {
    switch (status) {
      case 'Completed':
      case 'Shipped':
        return 'success';
      case 'InProgress':
        return 'info';
      case 'Delayed':
        return 'error';
      case 'Pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getSupplierStatusColor = (status: string): 'success' | 'warning' | 'error' | 'default' => {
    switch (status) {
      case 'Active':
        return 'success';
      case 'OnHold':
        return 'warning';
      case 'Suspended':
        return 'error';
      default:
        return 'default';
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

  // ========================================
  // Render Functions
  // ========================================

  // Loading state
  if (loading) {
    return (
      <Container maxWidth="xl">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  // Error state
  if (error) {
    return (
      <Container maxWidth="xl">
        <Alert severity="error" sx={{ mt: 4 }}>
          {error}
        </Alert>
      </Container>
    );
  }

  // No data state
  if (!stats?.exists) {
    return (
      <Container maxWidth="xl">
        <Alert severity="info" sx={{ mt: 4 }}>
          No production data available. Please generate data using the setup endpoint.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl">
      {/* Page Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Supply Chain Traceability
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Track materials, suppliers, and orders throughout the production lifecycle
        </Typography>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={currentTab} onChange={handleTabChange} aria-label="traceability tabs">
          <Tab icon={<InventoryIcon />} iconPosition="start" label="Batch Lookup" />
          <Tab icon={<SupplierIcon />} iconPosition="start" label="Supplier Impact" />
          <Tab icon={<OrderIcon />} iconPosition="start" label="Order Status" />
        </Tabs>
      </Box>

      {/* Tab 1: Batch Lookup */}
      {currentTab === 0 && (
        <Box>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Backward Traceability - Batch to Suppliers
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Select a production batch to trace materials back to their suppliers
              </Typography>

              <Autocomplete
                options={batches}
                getOptionLabel={(option) =>
                  `${option.batch_id} - ${option.part_number} (${formatDate(option.date)})`
                }
                value={selectedBatch}
                onChange={handleBatchSelect}
                renderInput={(params) => (
                  <TextField {...params} label="Select Production Batch" variant="outlined" />
                )}
                sx={{ mb: 3 }}
              />

              {batchLoading && (
                <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
                  <CircularProgress />
                </Box>
              )}

              {backwardTrace && !batchLoading && (
                <Box>
                  <Divider sx={{ my: 3 }} />

                  {/* Batch Information */}
                  <Typography variant="h6" gutterBottom>
                    Batch Information
                  </Typography>
                  <Grid container spacing={2} sx={{ mb: 3 }}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2" color="text.secondary">
                        Batch ID
                      </Typography>
                      <Typography variant="body1">{backwardTrace.batch.batch_id}</Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2" color="text.secondary">
                        Machine
                      </Typography>
                      <Typography variant="body1">{backwardTrace.batch.machine_name}</Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2" color="text.secondary">
                        Date
                      </Typography>
                      <Typography variant="body1">{formatDate(backwardTrace.batch.date)}</Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2" color="text.secondary">
                        Production
                      </Typography>
                      <Typography variant="body1">
                        {backwardTrace.batch.parts_produced} parts ({backwardTrace.batch.good_parts} good,{' '}
                        {backwardTrace.batch.scrap_parts} scrap)
                      </Typography>
                    </Grid>
                  </Grid>

                  {/* Materials Used */}
                  <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                    Materials Used ({backwardTrace.materials_trace.length})
                  </Typography>
                  <TableContainer component={Paper} sx={{ mb: 3 }}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Material</TableCell>
                          <TableCell>Lot Number</TableCell>
                          <TableCell align="right">Quantity Used</TableCell>
                          <TableCell>Supplier</TableCell>
                          <TableCell align="center">Quality Status</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {backwardTrace.materials_trace.map((material, index) => {
                          // Check if this lot is linked to any quality issues
                          const linkedIssues = backwardTrace.batch.quality_issues?.filter(
                            (issue: any) => issue.lot_number === material.lot_number
                          ) || [];
                          const hasQualityIssues = linkedIssues.length > 0;

                          return (
                            <TableRow
                              key={index}
                              sx={{
                                backgroundColor: hasQualityIssues ? 'error.light' : 'inherit',
                                opacity: hasQualityIssues ? 0.9 : 1
                              }}
                            >
                              <TableCell>
                                <Stack direction="row" spacing={1} alignItems="center">
                                  {hasQualityIssues && (
                                    <Warning color="error" fontSize="small" />
                                  )}
                                  <Typography variant="body2">
                                    {material.material_name}
                                  </Typography>
                                </Stack>
                              </TableCell>
                              <TableCell>
                                <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                                  {material.lot_number}
                                </Typography>
                              </TableCell>
                              <TableCell align="right">
                                {material.quantity_used} {material.unit}
                              </TableCell>
                              <TableCell>
                                {material.supplier?.name || 'Unknown'}
                              </TableCell>
                              <TableCell align="center">
                                {hasQualityIssues ? (
                                  <Chip
                                    icon={<Warning />}
                                    label={`${linkedIssues.length} issue${linkedIssues.length > 1 ? 's' : ''}`}
                                    color="error"
                                    size="small"
                                  />
                                ) : (
                                  <Chip
                                    icon={<CheckCircle />}
                                    label="OK"
                                    color="success"
                                    size="small"
                                    variant="outlined"
                                  />
                                )}
                              </TableCell>
                            </TableRow>
                          );
                        })}
                      </TableBody>
                    </Table>
                  </TableContainer>

                  {/* Suppliers Involved */}
                  <Typography variant="h6" gutterBottom>
                    Suppliers Involved ({backwardTrace.suppliers.length})
                  </Typography>
                  <Grid container spacing={2}>
                    {backwardTrace.suppliers.map((supplier) => (
                      <Grid item xs={12} md={6} key={supplier.id}>
                        <Card variant="outlined">
                          <CardContent>
                            <Stack direction="row" justifyContent="space-between" alignItems="start">
                              <Box>
                                <Typography variant="h6">{supplier.name}</Typography>
                                <Typography variant="body2" color="text.secondary">
                                  {supplier.id} - {supplier.type}
                                </Typography>
                              </Box>
                              <Chip
                                label={supplier.status}
                                color={getSupplierStatusColor(supplier.status)}
                                size="small"
                              />
                            </Stack>
                            <Divider sx={{ my: 1.5 }} />
                            <Grid container spacing={1}>
                              <Grid item xs={6}>
                                <Typography variant="caption" color="text.secondary">
                                  Quality Rating
                                </Typography>
                                <Typography variant="body2">
                                  {supplier.quality_metrics.quality_rating?.toFixed(1) || 'N/A'}%
                                </Typography>
                              </Grid>
                              <Grid item xs={6}>
                                <Typography variant="caption" color="text.secondary">
                                  Defect Rate
                                </Typography>
                                <Typography variant="body2">
                                  {supplier.quality_metrics.defect_rate?.toFixed(2) || 'N/A'}%
                                </Typography>
                              </Grid>
                            </Grid>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              )}

              {selectedBatch && !backwardTrace && !batchLoading && (
                <Alert severity="info">No traceability data found for this batch</Alert>
              )}
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Tab 2: Supplier Impact */}
      {currentTab === 1 && (
        <Box>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Supplier Quality Impact Analysis
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Analyze how supplier quality affects production batches and orders
              </Typography>

              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel id="supplier-select-label">Select Supplier</InputLabel>
                <Select
                  labelId="supplier-select-label"
                  id="supplier-select"
                  value={selectedSupplierId}
                  label="Select Supplier"
                  onChange={handleSupplierChange}
                >
                  <MenuItem value="">
                    <em>None</em>
                  </MenuItem>
                  {suppliers.map((supplier) => (
                    <MenuItem key={supplier.id} value={supplier.id}>
                      {supplier.name} ({supplier.id}) - Quality Rating:{' '}
                      {supplier.quality_metrics.quality_rating?.toFixed(1)}%
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {supplierLoading && (
                <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
                  <CircularProgress />
                </Box>
              )}

              {supplierImpact && !supplierLoading && (
                <Box>
                  <Divider sx={{ my: 3 }} />

                  {/* Supplier Summary Cards */}
                  <Grid container spacing={2} sx={{ mb: 3 }}>
                    <Grid item xs={12} sm={6} md={3}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h4" color="primary">
                          {supplierImpact.material_lots_supplied}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Material Lots Supplied
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h4" color="info.main">
                          {supplierImpact.affected_batches_count}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Batches Affected
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h4" color="warning.main">
                          {supplierImpact.quality_issues_count}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Quality Issues
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h4" color="error.main">
                          {formatCurrency(supplierImpact.estimated_cost_impact)}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Est. Cost Impact
                        </Typography>
                      </Paper>
                    </Grid>
                  </Grid>

                  {/* Supplier Details */}
                  <Card variant="outlined" sx={{ mb: 3 }}>
                    <CardContent>
                      <Stack direction="row" justifyContent="space-between" alignItems="start" sx={{ mb: 2 }}>
                        <Box>
                          <Typography variant="h6">{supplierImpact.supplier.name}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            {supplierImpact.supplier.id} - {supplierImpact.supplier.type}
                          </Typography>
                        </Box>
                        <Chip
                          label={supplierImpact.supplier.status}
                          color={getSupplierStatusColor(supplierImpact.supplier.status)}
                        />
                      </Stack>
                      <Grid container spacing={2}>
                        <Grid item xs={12} sm={4}>
                          <Typography variant="caption" color="text.secondary">
                            Quality Rating
                          </Typography>
                          <Typography variant="body1">
                            {supplierImpact.supplier.quality_metrics.quality_rating?.toFixed(1)}%
                          </Typography>
                        </Grid>
                        <Grid item xs={12} sm={4}>
                          <Typography variant="caption" color="text.secondary">
                            On-Time Delivery
                          </Typography>
                          <Typography variant="body1">
                            {supplierImpact.supplier.quality_metrics.on_time_delivery_rate?.toFixed(1)}%
                          </Typography>
                        </Grid>
                        <Grid item xs={12} sm={4}>
                          <Typography variant="caption" color="text.secondary">
                            Defect Rate
                          </Typography>
                          <Typography variant="body1">
                            {supplierImpact.supplier.quality_metrics.defect_rate?.toFixed(2)}%
                          </Typography>
                        </Grid>
                      </Grid>
                    </CardContent>
                  </Card>

                  {/* Affected Batches */}
                  {supplierImpact.affected_batches.length > 0 && (
                    <>
                      <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                        Affected Production Batches ({supplierImpact.affected_batches.length})
                      </Typography>
                      <TableContainer component={Paper}>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>Batch ID</TableCell>
                              <TableCell>Date</TableCell>
                              <TableCell>Machine</TableCell>
                              <TableCell align="right">Parts Produced</TableCell>
                              <TableCell align="right">Scrap</TableCell>
                              <TableCell>Materials Used</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {supplierImpact.affected_batches.map((batch) => (
                              <TableRow key={batch.batch_id}>
                                <TableCell>
                                  <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                                    {batch.batch_id}
                                  </Typography>
                                </TableCell>
                                <TableCell>{formatDate(batch.date)}</TableCell>
                                <TableCell>{batch.machine_name}</TableCell>
                                <TableCell align="right">{batch.parts_produced}</TableCell>
                                <TableCell align="right">
                                  {batch.scrap_parts > 0 && (
                                    <Chip label={batch.scrap_parts} size="small" color="error" />
                                  )}
                                  {batch.scrap_parts === 0 && batch.scrap_parts}
                                </TableCell>
                                <TableCell>{batch.materials_consumed.length} materials</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </>
                  )}

                  {/* Quality Issues */}
                  {supplierImpact.quality_issues.length > 0 && (
                    <>
                      <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                        Quality Issues ({supplierImpact.quality_issues.length})
                      </Typography>
                      <TableContainer component={Paper}>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>Batch ID</TableCell>
                              <TableCell>Date</TableCell>
                              <TableCell align="right">Defect Count</TableCell>
                              <TableCell>Defect Types</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {supplierImpact.quality_issues.map((issue, index) => (
                              <TableRow key={index}>
                                <TableCell>
                                  <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                                    {issue.batch_id}
                                  </Typography>
                                </TableCell>
                                <TableCell>{formatDate(issue.date)}</TableCell>
                                <TableCell align="right">
                                  <Chip label={issue.defect_count} size="small" color="error" />
                                </TableCell>
                                <TableCell>
                                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                                    {issue.defect_types.map((type, idx) => (
                                      <Chip key={idx} label={type} size="small" variant="outlined" />
                                    ))}
                                  </Box>
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </>
                  )}
                </Box>
              )}

              {selectedSupplierId && !supplierImpact && !supplierLoading && (
                <Alert severity="info">No impact data found for this supplier</Alert>
              )}
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Tab 3: Order Status */}
      {currentTab === 2 && (
        <Box>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Order Fulfillment Status
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Track customer orders and their production status
              </Typography>

              {/* Status Filter */}
              <FormControl sx={{ mb: 3, minWidth: 200 }}>
                <InputLabel id="order-status-filter-label">Filter by Status</InputLabel>
                <Select
                  labelId="order-status-filter-label"
                  id="order-status-filter"
                  value={orderStatusFilter}
                  label="Filter by Status"
                  onChange={handleOrderStatusFilterChange}
                >
                  <MenuItem value="all">All Statuses</MenuItem>
                  <MenuItem value="Pending">Pending</MenuItem>
                  <MenuItem value="InProgress">In Progress</MenuItem>
                  <MenuItem value="Completed">Completed</MenuItem>
                  <MenuItem value="Shipped">Shipped</MenuItem>
                  <MenuItem value="Delayed">Delayed</MenuItem>
                </Select>
              </FormControl>

              {/* Orders Summary */}
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={6} md={3}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h4" color="primary">
                      {filteredOrders.length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {orderStatusFilter === 'all' ? 'Total Orders' : `${orderStatusFilter} Orders`}
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h4" color="success.main">
                      {orders.filter((o) => o.status === 'Completed' || o.status === 'Shipped').length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Completed/Shipped
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h4" color="info.main">
                      {orders.filter((o) => o.status === 'InProgress').length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      In Progress
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h4" color="error.main">
                      {orders.filter((o) => o.status === 'Delayed').length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Delayed
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>

              {/* Orders Table */}
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Order #</TableCell>
                      <TableCell>Customer</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Priority</TableCell>
                      <TableCell>Due Date</TableCell>
                      <TableCell align="right">Value</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredOrders.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={7} align="center">
                          <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                            No orders found
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredOrders.map((order) => (
                        <TableRow
                          key={order.id}
                          hover
                          onClick={() => handleOrderSelect(order)}
                          sx={{ cursor: 'pointer' }}
                        >
                          <TableCell>
                            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                              {order.order_number}
                            </Typography>
                          </TableCell>
                          <TableCell>{order.customer}</TableCell>
                          <TableCell>
                            <Chip label={order.status} color={getOrderStatusColor(order.status)} size="small" />
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={order.priority}
                              variant="outlined"
                              size="small"
                              color={order.priority === 'Urgent' ? 'error' : 'default'}
                            />
                          </TableCell>
                          <TableCell>{formatDate(order.due_date)}</TableCell>
                          <TableCell align="right">{formatCurrency(order.total_value)}</TableCell>
                          <TableCell>
                            <Chip
                              icon={<ArrowForwardIcon />}
                              label="Details"
                              size="small"
                              variant="outlined"
                              onClick={() => handleOrderSelect(order)}
                            />
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>

              {/* Selected Order Details */}
              {selectedOrder && (
                <Box sx={{ mt: 3 }}>
                  <Divider sx={{ my: 3 }} />
                  <Typography variant="h6" gutterBottom>
                    Order Details - {selectedOrder.order_number}
                  </Typography>

                  <Grid container spacing={2} sx={{ mb: 3 }}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2" color="text.secondary">
                        Customer
                      </Typography>
                      <Typography variant="body1">{selectedOrder.customer}</Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2" color="text.secondary">
                        Status
                      </Typography>
                      <Chip label={selectedOrder.status} color={getOrderStatusColor(selectedOrder.status)} />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2" color="text.secondary">
                        Due Date
                      </Typography>
                      <Typography variant="body1">{formatDate(selectedOrder.due_date)}</Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2" color="text.secondary">
                        Total Value
                      </Typography>
                      <Typography variant="body1">{formatCurrency(selectedOrder.total_value)}</Typography>
                    </Grid>
                  </Grid>

                  {/* Order Items */}
                  <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                    Order Items ({selectedOrder.items.length})
                  </Typography>
                  <TableContainer component={Paper} sx={{ mb: 3 }}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Part Number</TableCell>
                          <TableCell align="right">Quantity</TableCell>
                          <TableCell align="right">Unit Price</TableCell>
                          <TableCell align="right">Total</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {selectedOrder.items.map((item, index) => (
                          <TableRow key={index}>
                            <TableCell>{item.part_number}</TableCell>
                            <TableCell align="right">{item.quantity}</TableCell>
                            <TableCell align="right">{formatCurrency(item.unit_price)}</TableCell>
                            <TableCell align="right">{formatCurrency(item.quantity * item.unit_price)}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>

                  {/* Production Batches for Order */}
                  {orderLoading && (
                    <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
                      <CircularProgress />
                    </Box>
                  )}

                  {orderBatches && !orderLoading && (
                    <>
                      <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                        Production Batches ({orderBatches.assigned_batches.length})
                      </Typography>
                      {orderBatches.assigned_batches.length > 0 ? (
                        <TableContainer component={Paper}>
                          <Table size="small">
                            <TableHead>
                              <TableRow>
                                <TableCell>Batch ID</TableCell>
                                <TableCell>Date</TableCell>
                                <TableCell>Machine</TableCell>
                                <TableCell>Part Number</TableCell>
                                <TableCell align="right">Parts Produced</TableCell>
                                <TableCell align="right">Good Parts</TableCell>
                                <TableCell align="right">Scrap</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {orderBatches.assigned_batches.map((batch) => (
                                <TableRow key={batch.batch_id}>
                                  <TableCell>
                                    <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                                      {batch.batch_id}
                                    </Typography>
                                  </TableCell>
                                  <TableCell>{formatDate(batch.date)}</TableCell>
                                  <TableCell>{batch.machine_name}</TableCell>
                                  <TableCell>{batch.part_number}</TableCell>
                                  <TableCell align="right">{batch.parts_produced}</TableCell>
                                  <TableCell align="right">{batch.good_parts}</TableCell>
                                  <TableCell align="right">
                                    {batch.scrap_parts > 0 ? (
                                      <Chip label={batch.scrap_parts} size="small" color="error" />
                                    ) : (
                                      batch.scrap_parts
                                    )}
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      ) : (
                        <Alert severity="info">No production batches assigned to this order yet</Alert>
                      )}

                      {/* Production Summary */}
                      <Paper sx={{ p: 2, mt: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Production Summary
                        </Typography>
                        <Grid container spacing={2}>
                          <Grid item xs={12} sm={4}>
                            <Typography variant="caption" color="text.secondary">
                              Total Parts Produced
                            </Typography>
                            <Typography variant="h6">{orderBatches.production_summary.total_produced}</Typography>
                          </Grid>
                          <Grid item xs={12} sm={4}>
                            <Typography variant="caption" color="text.secondary">
                              Good Parts
                            </Typography>
                            <Typography variant="h6" color="success.main">
                              {orderBatches.production_summary.total_good_parts}
                            </Typography>
                          </Grid>
                          <Grid item xs={12} sm={4}>
                            <Typography variant="caption" color="text.secondary">
                              Scrap Parts
                            </Typography>
                            <Typography variant="h6" color="error.main">
                              {orderBatches.production_summary.total_scrap}
                            </Typography>
                          </Grid>
                        </Grid>
                      </Paper>
                    </>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Box>
      )}
    </Container>
  );
};

export default TraceabilityPage;
