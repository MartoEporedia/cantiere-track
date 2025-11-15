'use client';

import { useEffect, useState } from 'react';
import { format } from 'date-fns';
import {
  getAttendances,
  getEmployees,
  getSites,
  clockIn,
  clockOut,
  getActiveAttendance,
  Attendance,
  Employee,
  Site,
} from '@/lib/api';

export default function AttendancePage() {
  const [attendances, setAttendances] = useState<Attendance[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [sites, setSites] = useState<Site[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showClockInModal, setShowClockInModal] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState<number | null>(null);
  const [selectedSite, setSelectedSite] = useState<number | null>(null);
  const [notes, setNotes] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [attendancesData, employeesData, sitesData] = await Promise.all([
        getAttendances({ limit: 100 }),
        getEmployees({ limit: 1000, is_active: true }),
        getSites({ limit: 1000, status: 'open' }),
      ]);
      setAttendances(attendancesData);
      setEmployees(employeesData.employees);
      setSites(sitesData.sites);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClockIn = async () => {
    if (!selectedEmployee || !selectedSite) {
      alert('Please select an employee and a site');
      return;
    }

    try {
      await clockIn({
        employee_id: selectedEmployee,
        site_id: selectedSite,
        notes,
      });
      setShowClockInModal(false);
      setSelectedEmployee(null);
      setSelectedSite(null);
      setNotes('');
      fetchData();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to clock in');
    }
  };

  const handleClockOut = async (attendanceId: number) => {
    try {
      await clockOut(attendanceId);
      fetchData();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to clock out');
    }
  };

  const calculateHours = (timestampIn: string, timestampOut?: string) => {
    const start = new Date(timestampIn);
    const end = timestampOut ? new Date(timestampOut) : new Date();
    const hours = (end.getTime() - start.getTime()) / (1000 * 60 * 60);
    return hours.toFixed(2);
  };

  if (isLoading) {
    return <div className="p-4">Loading...</div>;
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Attendance</h1>
          <p className="mt-2 text-sm text-gray-700">
            Track employee clock-in and clock-out times at construction sites.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button onClick={() => setShowClockInModal(true)} className="btn-primary">
            Clock In
          </button>
        </div>
      </div>

      {/* Active Attendances */}
      <div className="mt-8">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Currently Clocked In</h2>
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {attendances
              .filter((a) => !a.timestamp_out)
              .map((attendance) => (
                <li key={attendance.id}>
                  <div className="px-4 py-4 sm:px-6 flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-primary-600">
                          {attendance.employee?.name} {attendance.employee?.surname}
                        </p>
                        <div className="ml-2 flex-shrink-0 flex">
                          <p className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                            Active
                          </p>
                        </div>
                      </div>
                      <div className="mt-2 sm:flex sm:justify-between">
                        <div className="sm:flex">
                          <p className="flex items-center text-sm text-gray-500">
                            {attendance.site?.name} - {attendance.site?.address}
                          </p>
                        </div>
                        <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                          <p>
                            Clocked in at {format(new Date(attendance.timestamp_in), 'PPp')} (
                            {calculateHours(attendance.timestamp_in)} hours)
                          </p>
                        </div>
                      </div>
                    </div>
                    <div className="ml-4">
                      <button
                        onClick={() => handleClockOut(attendance.id)}
                        className="btn-danger"
                      >
                        Clock Out
                      </button>
                    </div>
                  </div>
                </li>
              ))}
          </ul>
          {attendances.filter((a) => !a.timestamp_out).length === 0 && (
            <div className="px-4 py-8 text-center text-gray-500">
              No active attendances
            </div>
          )}
        </div>
      </div>

      {/* Recent Attendances */}
      <div className="mt-8">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Completed</h2>
        <div className="flex flex-col">
          <div className="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
            <div className="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
              <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                <table className="min-w-full divide-y divide-gray-300">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">
                        Employee
                      </th>
                      <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Site</th>
                      <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                        Clock In
                      </th>
                      <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                        Clock Out
                      </th>
                      <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Hours</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 bg-white">
                    {attendances
                      .filter((a) => a.timestamp_out)
                      .slice(0, 20)
                      .map((attendance) => (
                        <tr key={attendance.id}>
                          <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                            {attendance.employee?.name} {attendance.employee?.surname}
                          </td>
                          <td className="px-3 py-4 text-sm text-gray-500">
                            {attendance.site?.name}
                          </td>
                          <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                            {format(new Date(attendance.timestamp_in), 'MMM d, HH:mm')}
                          </td>
                          <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                            {attendance.timestamp_out &&
                              format(new Date(attendance.timestamp_out), 'MMM d, HH:mm')}
                          </td>
                          <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                            {calculateHours(attendance.timestamp_in, attendance.timestamp_out)}h
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Clock In Modal */}
      {showClockInModal && (
        <div className="fixed z-10 inset-0 overflow-y-auto">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div
              className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
              onClick={() => setShowClockInModal(false)}
            ></div>

            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <h3 className="text-lg font-medium leading-6 text-gray-900 mb-4">Clock In</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Employee</label>
                    <select
                      className="input-field mt-1"
                      value={selectedEmployee || ''}
                      onChange={(e) => setSelectedEmployee(Number(e.target.value))}
                    >
                      <option value="">Select an employee</option>
                      {employees.map((emp) => (
                        <option key={emp.id} value={emp.id}>
                          {emp.name} {emp.surname} - {emp.badge_code}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Site</label>
                    <select
                      className="input-field mt-1"
                      value={selectedSite || ''}
                      onChange={(e) => setSelectedSite(Number(e.target.value))}
                    >
                      <option value="">Select a site</option>
                      {sites.map((site) => (
                        <option key={site.id} value={site.id}>
                          {site.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Notes (Optional)</label>
                    <textarea
                      className="input-field mt-1"
                      rows={3}
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                    />
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button onClick={handleClockIn} className="btn-primary ml-3">
                  Clock In
                </button>
                <button
                  type="button"
                  onClick={() => setShowClockInModal(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
