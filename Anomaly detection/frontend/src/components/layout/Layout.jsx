import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import { useEffect, useState } from 'react';
import GooeyNav from '@/components/ui/GooeyNav';
import LiquidEther from '@/components/backgrounds/LiquidEther';

const navItems = [
  { label: 'Dashboard', href: '/', path: '/' },
  { label: 'Detection', href: '/detection', path: '/detection' },
  { label: 'Models', href: '/models', path: '/models' },
  { label: 'Performance', href: '/performance', path: '/performance' },
  { label: 'Alerts', href: '/alerts', path: '/alerts' },
  { label: 'About', href: '/about', path: '/about' },
];

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    const idx = navItems.findIndex(item => item.path === location.pathname);
    if (idx !== -1) setActiveIndex(idx);
  }, [location.pathname]);

  const handleNavClick = (item, index) => {
    navigate(item.path);
  };

  return (
    <div style={{ position: 'relative', minHeight: '100vh' }}>
      {/* Liquid Ether background */}
      <div style={{ position: 'fixed', inset: 0, zIndex: 0 }}>
        <LiquidEther
          colors={['#1e1b4b', '#8b5cf6', '#06b6d4']}
          autoDemo={true}
          autoSpeed={0.4}
          autoIntensity={2.5}
          mouseForce={25}
          cursorSize={90}
          resolution={1.2}
        />
        {/* Overlay for readability - reduced opacity for prominence */}
        <div style={{ position: 'absolute', inset: 0, background: 'rgba(10, 10, 25, 0.4)' }} />
      </div>

      {/* Top navigation bar - increased opacity for legibility */}
      <header style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '12px 24px',
        background: 'rgba(10, 10, 25, 0.85)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(99, 102, 241, 0.2)',
      }}>
        <GooeyNav
          items={navItems}
          initialActiveIndex={activeIndex}
          animationTime={600}
          particleCount={15}
          particleDistances={[90, 10]}
          particleR={100}
          timeVariance={300}
          colors={[1, 2, 3, 1, 2, 3, 1, 4]}
          onItemClick={handleNavClick}
        />
      </header>

      {/* Main content */}
      <main style={{
        position: 'relative',
        zIndex: 10,
        paddingTop: '80px',
        paddingLeft: '32px',
        paddingRight: '32px',
        paddingBottom: '32px',
        maxWidth: '1400px',
        marginLeft: 'auto',
        marginRight: 'auto',
      }}>
        <Outlet />
      </main>
    </div>
  );
}
