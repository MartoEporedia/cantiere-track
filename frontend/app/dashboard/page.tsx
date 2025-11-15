'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getEmployees, getSites, getAttendances } from '@/lib/api';

export default function DashboardPage() {
  const [stats, setStats] = useState({
    totalEmployees: 0,
    activeEmployees: 0,
    totalSites: 0,
    openSites: 0,
    activeAttendances: 0,
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [employeesData, sitesData, attendancesData] = await Promise.all([
          getEmployees({ limit: 1000 }),
          getSites({ limit: 1000 }),
          getAttendances({ limit: 1000 }),
        ]);

        setStats({
          totalEmployees: employeesData.total,
          activeEmployees: employeesData.employees.filter((e: any) => e.is_active).length,
          totalSites: sitesData.total,
          openSites: sitesData.sites.filter((s: any) => s.status === 'open').length,
          activeAttendances: attendancesData.filter((a: any) => !a.timestamp_out).length,
        });
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg
                  className="h-6 w-6 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                  />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Employees</dt>
                  <dd className="flex items-baseline">
                    <div className="text-2xl font-semibold text-gray-900">{stats.totalEmployees}</div>
                    <div className="ml-2 text-sm text-gray-600">({stats.activeEmployees} active)</div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-5 py-3">
            <Link href="/dashboard/employees" className="text-sm text-primary-600 hover:text-primary-900">
              View all employees
            </Link>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg
                  className="h-6 w-6 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                  />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Construction Sites</dt>
                  <dd className="flex items-baseline">
                    <div className="text-2xl font-semibold text-gray-900">{stats.totalSites}</div>
                    <div className="ml-2 text-sm text-gray-600">({stats.openSites} open)</div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-5 py-3">
            <Link href="/dashboard/sites" className="text-sm text-primary-600 hover:text-primary-900">
              View all sites
            </Link>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg
                  className="h-6 w-6 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Active Attendances</dt>
                  <dd className="flex items-baseline">
                    <div className="text-2xl font-semibold text-gray-900">{stats.activeAttendances}</div>
                    <div className="ml-2 text-sm text-gray-600">currently clocked in</div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-5 py-3">
            <Link href="/dashboard/attendance" className="text-sm text-primary-600 hover:text-primary-900">
              View attendance
            </Link>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Link
            href="/dashboard/employees?action=new"
            className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow text-center"
          >
            <h3 className="text-lg font-medium text-gray-900">Add Employee</h3>
            <p className="mt-1 text-sm text-gray-500">Create a new employee profile</p>
          </Link>
          <Link
            href="/dashboard/sites?action=new"
            className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow text-center"
          >
            <h3 className="text-lg font-medium text-gray-900">Add Site</h3>
            <p className="mt-1 text-sm text-gray-500">Register a new construction site</p>
          </Link>
          <Link
            href="/dashboard/attendance?action=clock-in"
            className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow text-center"
          >
            <h3 className="text-lg font-medium text-gray-900">Clock In</h3>
            <p className="mt-1 text-sm text-gray-500">Record employee arrival</p>
          </Link>
          <Link
            href="/dashboard/reports"
            className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow text-center"
          >
            <h3 className="text-lg font-medium text-gray-900">View Reports</h3>
            <p className="mt-1 text-sm text-gray-500">Generate attendance reports</p>
          </Link>
        </div>
      </div>
    </div>
  );
}
