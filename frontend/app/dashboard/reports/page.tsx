'use client';

import { useState } from 'react';
import { format } from 'date-fns';
import {
  getEmployeeReport,
  getSiteReport,
  downloadEmployeeReportCSV,
  downloadSiteReportCSV,
  getEmployees,
  getSites,
} from '@/lib/api';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid, LineChart, Line, Area, AreaChart } from 'recharts';

// Color palette for charts
const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];

export default function ReportsPage() {
  const [reportType, setReportType] = useState<'employee' | 'site'>('employee');
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [reportData, setReportData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [employees, setEmployees] = useState<any[]>([]);
  const [sites, setSites] = useState<any[]>([]);

  const fetchOptions = async () => {
    try {
      const [employeesData, sitesData] = await Promise.all([
        getEmployees({ limit: 1000 }),
        getSites({ limit: 1000 }),
      ]);
      setEmployees(employeesData.employees);
      setSites(sitesData.sites);
    } catch (error) {
      console.error('Failed to fetch options:', error);
    }
  };

  useState(() => {
    fetchOptions();
  });

  const handleGenerateReport = async () => {
    if (!selectedId) {
      alert('Please select an employee or site');
      return;
    }

    setIsLoading(true);
    try {
      const params = {
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
      };

      let data;
      if (reportType === 'employee') {
        data = await getEmployeeReport(selectedId, params);
      } else {
        data = await getSiteReport(selectedId, params);
      }
      setReportData(data);
    } catch (error) {
      alert('Failed to generate report');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadCSV = async () => {
    if (!selectedId) return;

    try {
      const params = {
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
      };

      let blob;
      if (reportType === 'employee') {
        blob = await downloadEmployeeReportCSV(selectedId, params);
      } else {
        blob = await downloadSiteReportCSV(selectedId, params);
      }

      // Create download link
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${reportType}_${selectedId}_report.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      alert('Failed to download CSV');
    }
  };

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Reports</h1>
          <p className="mt-2 text-sm text-gray-700">
            Generate attendance reports for employees or construction sites.
          </p>
        </div>
      </div>

      {/* Report Configuration */}
      <div className="mt-8 bg-white shadow sm:rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Generate Report</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700">Report Type</label>
            <select
              className="input-field mt-1"
              value={reportType}
              onChange={(e) => {
                setReportType(e.target.value as 'employee' | 'site');
                setSelectedId(null);
                setReportData(null);
              }}
            >
              <option value="employee">Employee Report</option>
              <option value="site">Site Report</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              {reportType === 'employee' ? 'Select Employee' : 'Select Site'}
            </label>
            <select
              className="input-field mt-1"
              value={selectedId || ''}
              onChange={(e) => setSelectedId(Number(e.target.value))}
            >
              <option value="">Select...</option>
              {reportType === 'employee'
                ? employees.map((emp) => (
                    <option key={emp.id} value={emp.id}>
                      {emp.name} {emp.surname} - {emp.badge_code}
                    </option>
                  ))
                : sites.map((site) => (
                    <option key={site.id} value={site.id}>
                      {site.name}
                    </option>
                  ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">From Date</label>
            <input
              type="date"
              className="input-field mt-1"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">To Date</label>
            <input
              type="date"
              className="input-field mt-1"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
            />
          </div>
        </div>

        <div className="mt-6 flex gap-4">
          <button onClick={handleGenerateReport} disabled={isLoading} className="btn-primary">
            {isLoading ? 'Generating...' : 'Generate Report'}
          </button>
          {reportData && (
            <button onClick={handleDownloadCSV} className="btn-secondary">
              Download CSV
            </button>
          )}
        </div>
      </div>

      {/* Report Results */}
      {reportData && (
        <div className="mt-8 bg-white shadow sm:rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Report Results</h2>

          {/* Summary */}
          <div className="mb-6">
            <h3 className="text-md font-medium text-gray-900 mb-2">Summary</h3>
            {reportType === 'employee' ? (
              <div>
                <p className="text-sm text-gray-700">
                  <span className="font-medium">Employee:</span> {reportData.employee?.name}{' '}
                  {reportData.employee?.surname} ({reportData.employee?.badge_code})
                </p>
                <p className="text-sm text-gray-700">
                  <span className="font-medium">Role:</span> {reportData.employee?.role}
                </p>
                <p className="text-sm text-gray-700">
                  <span className="font-medium">Total Hours:</span> {reportData.summary?.total_hours}h
                </p>
                <p className="text-sm text-gray-700">
                  <span className="font-medium">Total Attendances:</span>{' '}
                  {reportData.summary?.total_attendances}
                </p>
                <p className="text-sm text-gray-700">
                  <span className="font-medium">Sites Visited:</span>{' '}
                  {reportData.summary?.sites_visited}
                </p>
              </div>
            ) : (
              <div>
                <p className="text-sm text-gray-700">
                  <span className="font-medium">Site:</span> {reportData.site?.name}
                </p>
                <p className="text-sm text-gray-700">
                  <span className="font-medium">Address:</span> {reportData.site?.address}
                </p>
                <p className="text-sm text-gray-700">
                  <span className="font-medium">Total Hours:</span> {reportData.summary?.total_hours}h
                </p>
                <p className="text-sm text-gray-700">
                  <span className="font-medium">Total Attendances:</span>{' '}
                  {reportData.summary?.total_attendances}
                </p>
                <p className="text-sm text-gray-700">
                  <span className="font-medium">Unique Employees:</span>{' '}
                  {reportData.summary?.unique_employees}
                </p>
              </div>
            )}
          </div>

          {/* Charts and Aggregation */}
          {((reportType === 'site' && reportData.role_aggregation?.length > 0) ||
            (reportType === 'employee' && reportData.site_aggregation?.length > 0)) && (
            <div className="mb-6">
              <h3 className="text-md font-medium text-gray-900 mb-4">
                {reportType === 'site' ? 'Hours by Role' : 'Hours by Site'}
              </h3>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Pie Chart */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Distribution</h4>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={reportType === 'site'
                          ? reportData.role_aggregation.map((item: any) => ({ name: item.role, value: item.hours }))
                          : reportData.site_aggregation.map((item: any) => ({ name: item.site, value: item.hours }))}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name}: ${percent ? (percent * 100).toFixed(0) : 0}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {(reportType === 'site' ? reportData.role_aggregation : reportData.site_aggregation).map((_: any, index: number) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value: any) => `${value}h`} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                {/* Bar Chart */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Comparison</h4>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart
                      data={reportType === 'site'
                        ? reportData.role_aggregation.map((item: any) => ({ name: item.role, hours: item.hours }))
                        : reportData.site_aggregation.map((item: any) => ({ name: item.site, hours: item.hours }))}
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                      <YAxis label={{ value: 'Hours', angle: -90, position: 'insideLeft' }} />
                      <Tooltip formatter={(value: any) => `${value}h`} />
                      <Bar dataKey="hours" fill="#3b82f6" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Aggregation Table */}
              <div className="mt-6">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Detailed Breakdown</h4>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-300">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">
                          {reportType === 'site' ? 'Role' : 'Site'}
                        </th>
                        <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                          Total Hours
                        </th>
                        <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                          Percentage
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 bg-white">
                      {(reportType === 'site' ? reportData.role_aggregation : reportData.site_aggregation).map((item: any, index: number) => {
                        const percentage = (item.hours / reportData.summary.total_hours * 100).toFixed(1);
                        return (
                          <tr key={index}>
                            <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                              <span className="inline-flex items-center">
                                <span
                                  className="w-3 h-3 rounded-full mr-2"
                                  style={{ backgroundColor: COLORS[index % COLORS.length] }}
                                ></span>
                                {reportType === 'site' ? item.role : item.site}
                              </span>
                            </td>
                            <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                              {item.hours}h
                            </td>
                            <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                              {percentage}%
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Time Trend and Day of Week Charts */}
          {reportData.attendances?.length > 0 && (
            <div className="mb-6">
              <h3 className="text-md font-medium text-gray-900 mb-4">Time Analysis</h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Time Trend Chart */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Hours Worked Over Time</h4>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart
                      data={(() => {
                        // Aggregate hours by date
                        const hoursByDate: { [key: string]: number } = {};
                        reportData.attendances.forEach((att: any) => {
                          if (att.timestamp_out && att.hours_worked) {
                            const date = format(new Date(att.timestamp_in), 'yyyy-MM-dd');
                            if (!hoursByDate[date]) {
                              hoursByDate[date] = 0;
                            }
                            hoursByDate[date] += att.hours_worked;
                          }
                        });

                        // Convert to array and sort by date
                        return Object.entries(hoursByDate)
                          .map(([date, hours]) => ({ date, hours: parseFloat(hours.toFixed(2)) }))
                          .sort((a, b) => a.date.localeCompare(b.date));
                      })()}
                      margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                    >
                      <defs>
                        <linearGradient id="colorHours" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                          <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="date"
                        tickFormatter={(date) => format(new Date(date), 'MMM dd')}
                      />
                      <YAxis label={{ value: 'Hours', angle: -90, position: 'insideLeft' }} />
                      <Tooltip
                        labelFormatter={(date) => format(new Date(date), 'PPP')}
                        formatter={(value: any) => [`${value}h`, 'Hours']}
                      />
                      <Area
                        type="monotone"
                        dataKey="hours"
                        stroke="#3b82f6"
                        fillOpacity={1}
                        fill="url(#colorHours)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>

                {/* Day of Week Chart */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Average Hours by Day of Week</h4>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart
                      data={(() => {
                        // Aggregate hours by day of week
                        const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
                        const hoursByDayOfWeek: { [key: number]: { total: number; count: number } } = {};

                        reportData.attendances.forEach((att: any) => {
                          if (att.timestamp_out && att.hours_worked) {
                            const dayOfWeek = new Date(att.timestamp_in).getDay();
                            if (!hoursByDayOfWeek[dayOfWeek]) {
                              hoursByDayOfWeek[dayOfWeek] = { total: 0, count: 0 };
                            }
                            hoursByDayOfWeek[dayOfWeek].total += att.hours_worked;
                            hoursByDayOfWeek[dayOfWeek].count += 1;
                          }
                        });

                        // Convert to array with averages
                        return dayNames.map((day, index) => ({
                          day: day.substring(0, 3), // Short day name
                          hours: hoursByDayOfWeek[index]
                            ? parseFloat((hoursByDayOfWeek[index].total / hoursByDayOfWeek[index].count).toFixed(2))
                            : 0
                        }));
                      })()}
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="day" />
                      <YAxis label={{ value: 'Avg Hours', angle: -90, position: 'insideLeft' }} />
                      <Tooltip formatter={(value: any) => [`${value}h`, 'Average Hours']} />
                      <Bar dataKey="hours" fill="#10b981" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}

          {/* Attendances Table */}
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-300">
              <thead className="bg-gray-50">
                <tr>
                  {reportType === 'employee' ? (
                    <>
                      <th className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">
                        Site
                      </th>
                      <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                        Address
                      </th>
                    </>
                  ) : (
                    <>
                      <th className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">
                        Employee
                      </th>
                      <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                        Badge
                      </th>
                      <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Role</th>
                    </>
                  )}
                  <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    Clock In
                  </th>
                  <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    Clock Out
                  </th>
                  <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Hours</th>
                  <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {reportData.attendances?.map((att: any) => (
                  <tr key={att.id}>
                    {reportType === 'employee' ? (
                      <>
                        <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                          {att.site_name}
                        </td>
                        <td className="px-3 py-4 text-sm text-gray-500">{att.site_address}</td>
                      </>
                    ) : (
                      <>
                        <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                          {att.employee_name}
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                          {att.employee_badge}
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                          {att.employee_role}
                        </td>
                      </>
                    )}
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                      {format(new Date(att.timestamp_in), 'PPp')}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                      {att.timestamp_out ? format(new Date(att.timestamp_out), 'PPp') : '-'}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                      {att.hours_worked ? `${att.hours_worked}h` : '-'}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                      <span
                        className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                          att.status === 'completed'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {att.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
