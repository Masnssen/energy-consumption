import React, { useState, useEffect } from 'react';

const VmSelection = ({ vms, onVMSelect }) => {
  const [selectedVMs, setSelectedVMs] = useState({});

  useEffect(() => {
    onVMSelect(selectedVMs);
  }, [selectedVMs, onVMSelect]);

  const handleVMSelect = (serverKey, vmName, vmIp, isChecked) => {
    setSelectedVMs(prevState => {
      const newState = { ...prevState };

      if (isChecked) {
        if (!(serverKey in newState)) {
          newState[serverKey] = [];
        }
        newState[serverKey].push([vmName, vmIp]);
      } else {
        if (serverKey in newState) {
          newState[serverKey] = newState[serverKey].filter(vm => vm[1] !== vmIp);
          if (newState[serverKey].length === 0) {
            delete newState[serverKey];
          }
        }
      }
      
      return newState;
    });
  };

  return (
    <div className="vm-selection">
      <h3>Select VMs</h3>
      {Object.keys(vms).map(serverKey => (
        <div key={serverKey}>
          <h4>{serverKey}</h4>
          {Array.isArray(vms[serverKey]) ? (
            vms[serverKey].map((vm, index) => (
              <div key={index}>
                <label>
                  <input
                    type="checkbox"
                    value={vm[1]}
                    onChange={(e) => handleVMSelect(serverKey, vm[0], vm[1], e.target.checked)}
                  />
                  {vm[0]} ({vm[1]})
                </label>
              </div>
            ))
          ) : (
            <p>No VMs available</p>
          )}
        </div>
      ))}
    </div>
  );
};

export default VmSelection;
