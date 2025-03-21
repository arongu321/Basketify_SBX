import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate, useLocation } from 'react-router-dom';
import { ACCESS_TOKEN } from '../utils/constants';

function SearchInterface() {
  const [message, setMessage] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const navigate = useNavigate();
  const location = useLocation();

  // get access token from localStorage, should already be set during login
  const accessToken = localStorage.getItem(ACCESS_TOKEN);

  const setFavorite = location.state?.setFavorite;  // 'player' or 'team'
  const searchType = setFavorite || 'player'; // default to 'player' if no state is passed

  useEffect(() => {
    axios.get('http://localhost:8000/api/search-message/')
      .then(response => {
        setMessage(response.data.message);
      })
      .catch(error => {
        console.error("There was an error fetching the search interface message:", error);
      });
  }, []);

  // perform the search based on search term and search type (player or team)
  const handleSearch = () => {
    const url = searchType === 'player'
      ? 'http://localhost:8000/api/search-player'
      : 'http://localhost:8000/api/search-team';

    axios.get(url, { params: { name: searchTerm } })
      .then(response => {
        if (searchType === 'player') {
          setSearchResults(response.data.players);
        } else {
          setSearchResults(response.data.teams);
        }
      })
      .catch(error => {
        console.error("Error fetching search results:", error);
      });
  };

  // handle click on player/team name, either setting it as favorite or navigating to stats page
  const handleClick = (name) => {
    if (setFavorite) {
      axios.post('http://localhost:8000/accounts/set-favorite/', {
        type: setFavorite,
        name: name
      }, {
        headers: {
          'Authorization': `Bearer ${accessToken}` // django checks if user logged in so pass token
        }
      })
        .then(() => {
          navigate('/'); // return to dashboard after saving
        })
        .catch(error => {
          console.error("Error saving favorite:", error);
        });
    } else {
      // normal navigation to stats page (not selecting a favorite)
      navigate(`/stats/${searchType}/${name}`);
    }
  };

  return (
    <div>
      <h1>Search Interface Page</h1>
      <p>{message}</p>

      {/* Conditional rendering of search type buttons */}
      {!setFavorite && (
        <div>
          <button onClick={() => { 
            setSearchResults([]); // clear results when switching to player search
            navigate('/search', { state: { setFavorite: 'player' } });
          }}>
            Search Players
          </button>
          <button onClick={() => { 
            setSearchResults([]); // clear results when switching to team search
            navigate('/search', { state: { setFavorite: 'team' } });
          }}>
            Search Teams
          </button>
        </div>
      )}

      {/* Search Input */}
      <div>
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder={`Enter ${searchType} name`}
          onKeyDown={(e) => {  // do a search on enter key press
            if (e.key === 'Enter') {
              handleSearch();
            }
          }}
        />
        <button onClick={handleSearch}>Search</button>
      </div>

      {/* Display Search Results */}
      {searchResults.length > 0 && (
        <div>
          <h3>Search Results:</h3>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                {searchType === 'player' && <th>Position</th>}
                {searchType === 'player' && <th>Team</th>}
                {searchType === 'team' && <th>Location</th>}
              </tr>
            </thead>
            <tbody>
              {searchResults.map((result, index) => (
                <tr key={index} onClick={() => handleClick(result.name)}>
                  <td 
                    style={{
                      color: 'blue', 
                      textDecoration: 'underline', 
                      cursor: 'pointer'
                    }}
                  >
                    {result.name}
                  </td>
                  {searchType === 'player' && <td>{result.position}</td>}
                  {searchType === 'player' && <td>{result.team}</td>}
                  {searchType === 'team' && <td>{result.location}</td>}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* No results message */}
      {searchResults.length === 0 && searchTerm && (
        <div>
          <h3>No results found for "{searchTerm}".</h3>
        </div>
      )}
    </div>
  );
}

export default SearchInterface;
