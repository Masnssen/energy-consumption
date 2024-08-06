import React, { useState } from 'react';
import ServerSelection from './components/ServerSelection';
import VMSelection from './components/VmSelection';
import DateRangePicker from './components/DateRangeSelection';
import EnergyDisplay from './components/EnergyDisplay';
import './index.css';
import {useManageServers, handleServerSelect, handleSubmit} from './manage.js'


const App = () => {
  const [servers, setServers] = useState([]);
  const [vms, setVMs] = useState([]); 
  const [selectedServers, setSelectedServers] = useState([]);
  const [selectedVMs, setSelectedVMs] = useState({});
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  const [energyData, setEnergyData] = useState(null);
  const [errors, setErrors] = useState({});

  useManageServers(setServers)


  const handleServerSelectWrapper = async (selected) => {
    await handleServerSelect(selected, servers, setSelectedServers, setVMs);
  };
  
  const handleDateChange = (type, value) => {
    setDateRange(prevState => ({ ...prevState, [type]: value }));
  };


  const handleSubmitWrapper = async () => {
    // Perform validation
    const newErrors = {};
    console.log(dateRange)
    if (!dateRange.start) newErrors.start = 'Start date and time are required';
    if (!dateRange.end) newErrors.end = 'End date and time are required';
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    
    await handleSubmit(selectedVMs, dateRange, setEnergyData);

  };
  
  

  return (
    <div className="App">
      <h1>Energy Consumption Dashboard</h1>
      <ServerSelection servers={servers} onServerSelect={handleServerSelectWrapper} />
      <VMSelection vms={vms} onVMSelect={setSelectedVMs}/>
      <DateRangePicker onDateChange={handleDateChange} errors={errors} />
      <button  className="submit_button" onClick={handleSubmitWrapper}>Submit</button>
      <EnergyDisplay energyData={energyData} />
    </div>
  );
};

export default App;
