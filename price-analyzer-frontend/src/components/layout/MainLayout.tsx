import React from 'react';
import { Box, CssBaseline, Toolbar, AppBar, Typography, Container } from '@mui/material';
import { ThemeProvider } from '@mui/material/styles';
import { theme } from '../../theme/theme';

interface MainLayoutProps {
  children: React.ReactNode;
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ display: 'flex', minHeight: '100vh' }}>
        <CssBaseline />
        <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Paraguai Price Analyzer
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="body2">
                Dólar: R$ --,--
              </Typography>
              <Typography variant="caption" sx={{ 
                bgcolor: 'success.light', 
                color: 'white',
                px: 1,
                borderRadius: 1
              }}>
                Atualizado: --:--
              </Typography>
            </Box>
          </Toolbar>
        </AppBar>
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: 3,
            width: '100%',
            mt: 8, // Space for the app bar
          }}
        >
          <Container maxWidth="xl">
            {children}
          </Container>
        </Box>
      </Box>
    </ThemeProvider>
  );
};

export default MainLayout;
