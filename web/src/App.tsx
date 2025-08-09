import { Outlet } from "react-router-dom";
import Navigation from "./components/navigation";
import Footer from "./components/footer";
import ErrorBoundary from "./components/ErrorBoundary";
import { AuthProvider } from "./context/AuthContext";

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <div className="flex flex-col min-h-screen">
          <Navigation />
          <main className="flex-grow">
            <Outlet />
          </main>
          <Footer />
        </div>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
