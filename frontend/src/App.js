import {useEffect} from 'react'

import AuthProvider from 'context/AuthProvider'
import Home from './pages/Home'
import Register from './pages/Register'

import LoginModal from './components/LoginModal'


import {
  createBrowserRouter, 
  RouterProvider,
  Link
} from "react-router-dom"


const NoMatch = () => {
  <div>
    <h2>No page could be found at the entered route.</h2>
    <p>Please return to the <Link to="/">home page</Link></p>
  </div>
}

const router = createBrowserRouter([
  {
    path: "/", 
    element: <Home />,
    children: [
      {
        path: "login",
        element: <LoginModal />
      }
    ]
  }, 
  {
    path: "*",
    element: <NoMatch />
  }
])

const App = () => {
  // const location = useLocation()

  // const state = location.state
  return (
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  )


}


export default App;
