import { Link } from 'react-router-dom';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import { ThemeProvider, createTheme } from '@mui/material/styles';


const darkTheme = createTheme({
    palette: {
        mode: 'dark',
        primary: {
        main: '#1976d2',
        },
    },
});

export default function ButtonAppBar() {
  return (
    <Box sx={{ flexGrow: 1 }}>
        <ThemeProvider theme={darkTheme}>
            <AppBar position="static">
                <Toolbar variant="dense">
                    <IconButton
                        size="large"
                        edge="start"
                        color="inherit"
                        aria-label="menu"
                        sx={{ mr: 2 }}
                    >
                        <MenuIcon />
                    </IconButton>
                    <Typography variant="h6" component="div" align="left" sx={{ flexGrow: 1 }}>
                        Smart Security Camera
                    </Typography>
                    <Button component={Link} to="/videos" variant="contained" color="primary">
                        Videos
                    </Button>
                </Toolbar>
            </AppBar>
        </ThemeProvider>
    </Box>
  );
}