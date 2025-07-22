import { Grid as MuiGrid, GridProps } from '@mui/material';

// Re-export MUI Grid components with proper TypeScript types
export const Grid = MuiGrid;

// Grid item component
export const GridItem = ({ children, ...props }: GridProps) => (
  <MuiGrid {...props}>
    {children}
  </MuiGrid>
);

// Grid container component
export const GridContainer = ({ children, ...props }: Omit<GridProps, 'item'>) => (
  <MuiGrid container {...props}>
    {children}
  </MuiGrid>
);
