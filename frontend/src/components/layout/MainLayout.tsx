import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Box,
  CssBaseline,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Settings as MachinesIcon,
  Warning as AlertsIcon,
  LocalShipping as TraceabilityIcon,
  Chat as ChatIcon,
} from '@mui/icons-material';

const DRAWER_WIDTH = 240;

interface NavigationItem {
  label: string;
  path: string;
  icon: React.ReactElement;
}

const navigationItems: NavigationItem[] = [
  { label: 'Dashboard', path: '/', icon: <DashboardIcon /> },
  { label: 'Machines', path: '/machines', icon: <MachinesIcon /> },
  { label: 'Alerts', path: '/alerts', icon: <AlertsIcon /> },
  { label: 'Traceability', path: '/traceability', icon: <TraceabilityIcon /> },
  { label: 'AI Chat', path: '/chat', icon: <ChatIcon /> },
];

/**
 * MainLayout component provides the primary application layout with responsive navigation.
 *
 * Features:
 * - MUI AppBar with title and menu toggle
 * - Persistent Drawer navigation on desktop (md+)
 * - Temporary (overlay) Drawer navigation on mobile
 * - Responsive design adapting to screen size
 * - Active route highlighting in navigation
 * - Main content area using React Router Outlet
 */
const MainLayout: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  // Determine if screen is mobile (smaller than md breakpoint)
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Mobile: drawer starts closed, Desktop: drawer starts open
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);

  // Toggle mobile drawer open/close
  const handleDrawerToggle = () => {
    setMobileDrawerOpen(!mobileDrawerOpen);
  };

  // Navigate to a route and close mobile drawer
  const handleNavigate = (path: string) => {
    navigate(path);
    if (isMobile) {
      setMobileDrawerOpen(false);
    }
  };

  // Drawer content shared between mobile and desktop
  const drawerContent = (
    <div>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          Factory Agent
        </Typography>
      </Toolbar>
      <List>
        {navigationItems.map((item) => {
          // Highlight active route
          const isActive = location.pathname === item.path;

          return (
            <ListItem key={item.path} disablePadding>
              <ListItemButton
                selected={isActive}
                onClick={() => handleNavigate(item.path)}
              >
                <ListItemIcon sx={{ color: isActive ? 'primary.main' : 'inherit' }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.label} />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />

      {/* AppBar - Top navigation bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${DRAWER_WIDTH}px)` },
          ml: { md: `${DRAWER_WIDTH}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            AI-Powered Factory Operations Dashboard
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Navigation Drawer */}
      <Box
        component="nav"
        sx={{ width: { md: DRAWER_WIDTH }, flexShrink: { md: 0 } }}
        aria-label="navigation"
      >
        {/* Mobile drawer - temporary overlay */}
        <Drawer
          variant="temporary"
          open={mobileDrawerOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better mobile performance
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: DRAWER_WIDTH,
            },
          }}
        >
          {drawerContent}
        </Drawer>

        {/* Desktop drawer - persistent */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: DRAWER_WIDTH,
            },
          }}
          open
        >
          {drawerContent}
        </Drawer>
      </Box>

      {/* Main content area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${DRAWER_WIDTH}px)` },
        }}
      >
        {/* Toolbar spacing to push content below AppBar */}
        <Toolbar />

        {/* React Router Outlet - renders matched route component */}
        <Outlet />
      </Box>
    </Box>
  );
};

export default MainLayout;
