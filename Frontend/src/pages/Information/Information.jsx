import React, { useState, useEffect } from "react";
import { Sidebar } from "../../components";
import axios from "axios";

export default function Information() {
  const [people, setPeople] = useState([]);
  useEffect(() => {
    // Gọi API từ Flask server khi component được tạo
    axios
      .get("http://localhost:5000/get_detected_data")
      .then((response) => {
        setPeople(response.data.detected_data);
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
      });
  }, []);
  return (
    <>
      <section className="flex">
        <Sidebar />
        <div className="w-full">
          {/*  Attendence section  */}
          <div className="mx-28 mt-10">
            <h3 className="font-bold text-2xl">Attendence Status</h3>
          </div>
          <div className="mx-28 my-10 px-7 rounded-xl bg-gray-300">
            <ul role="list" className="divide-y divide-gray-100">
              {people.map((person, index) => (
                <li key={index} className="flex justify-between gap-x-6 py-5">
                  <div className="flex min-w-0 gap-x-4">
                    <img
                      className="h-12 w-12 flex-none rounded-full bg-gray-50"
                      src={person.imageUrl}
                      alt=""
                    />
                    <div className="min-w-0 flex-auto">
                      <p className="text-sm font-semibold leading-6 text-gray-900">
                        {/* name người đã được nhận diện */}
                        {person.result}
                      </p>
                      <p className="mt-1 truncate text-xs leading-5 text-gray-500">
                        {person.email}
                      </p>
                    </div>
                  </div>
                  <div className="hidden shrink-0 sm:flex sm:flex-col sm:items-end">
                    <p className="text-sm leading-6 text-gray-900">
                      {person.role}
                    </p>
                    {person.lastSeen ? (
                      <p className="mt-1 text-xs leading-5 text-gray-500">
                        Last seen{" "}
                        <time dateTime={person.lastSeenDateTime}>
                          {person.lastSeen}
                        </time>
                      </p>
                    ) : (
                      <div className="mt-1 flex items-center gap-x-1.5">
                        <div className="flex-none rounded-full bg-green-500/20 p-1">
                          <div className="h-1.5 w-1.5 rounded-full bg-green-700" />
                        </div>
                        <p className="text-xs leading-5 text-gray-500">
                          Attendence
                        </p>
                      </div>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>
    </>
  );
}
