import React, { useState } from 'react';


const ServerSelection = ({ servers, onServerSelect }) => {

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedServers, setSelectedServers] = useState([]);

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleServerSelect = (serverId) => {
    if (selectedServers.includes(serverId)) {
      setSelectedServers(selectedServers.filter(id => id !== serverId));
    } else {
      setSelectedServers([...selectedServers, serverId]);
    }
  };

  const filteredServers = servers.filter(server =>
    server.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="server-selection">
      <h3>Select communication infrastructure</h3>
      <input
        type="text"
        placeholder="Search servers..."
        value={searchTerm}
        onChange={handleSearchChange}
      />

      {filteredServers.map(server => (
        <div key={server.id}>
          <label>
            <input
              type="checkbox"
              checked={selectedServers.includes(server.id)}
              onChange={() => handleServerSelect(server.id)}
            />
            {server.name} {server.ip}
          </label>
        </div>
      ))}

      <button onClick={() => onServerSelect(selectedServers)}>Select</button>
    </div>
  );
};



export default ServerSelection;
