"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";

import { Dispatch, SetStateAction } from "react";

import { Message } from "../types/chat";

import {
  regenerateEmail,
  sendEmail
} from "../services/chatApi";

interface MeetingMetadata {
  date: string | null;
  time: string | null;
  comments: string | null;
  requires_meeting_link: boolean;
}


interface EmailCardProps {
  draft_id: number;
  email_id: string;
  subject: string;
  body: string;
  sessionID: string;
  meeting_metadata?: MeetingMetadata;
  setLoading: Dispatch<SetStateAction<boolean>>;
  setMessages: Dispatch<SetStateAction<Message[]>>;

}



export interface EmailMeetingDetails {
  requires_meeting_link: boolean;
  date: string;
  time: string;
  comments: string;
}




export default function EmailCard({
  draft_id,
  email_id,
  subject,
  body,
  meeting_metadata,
  setLoading,
  setMessages,
  sessionID

}: EmailCardProps) {



  const [showDetails, setShowDetails] =
    useState(false);

  const initialDetails = {
    requires_meeting_link:
      meeting_metadata?.requires_meeting_link ?? false,

    date:
      meeting_metadata?.date ?? "",

    time:
      meeting_metadata?.time ?? "",

    comments:
      meeting_metadata?.comments ?? "",
  };

  const [formDetails, setFormDetails] =
    useState<EmailMeetingDetails>(initialDetails);

  const [appliedDetails, setAppliedDetails] =
    useState<EmailMeetingDetails>(initialDetails);

  const handleApplyChanges = () => {
    setAppliedDetails(formDetails);
    setShowDetails(false);
  };

  const buildMeetingPreview = () => {
    const lines: string[] = [];

    if (appliedDetails.date) {
      lines.push(
        `- Date: ${appliedDetails.date}`
      );
    }

    if (appliedDetails.time) {
      lines.push(
        `- Time: ${appliedDetails.time}`
      );
    }

    if (appliedDetails.requires_meeting_link) {
      lines.push(
        `- Meeting Link: To be generated`
      );
    }

    if (appliedDetails.comments) {
      lines.push(
        `- Notes: ${appliedDetails.comments}`
      );
    }

    if (lines.length === 0) {
      return "";
    }

    return `
### Meeting Details

${lines.join("\n")}
`;
  };



  const handleRegenerate = async (
    draftId: number,
    appliedDetails: EmailMeetingDetails
  ) => {



    // Add user message
    setMessages(prev => [
      ...prev,
      {
        role: "user",
        content: "Regenerate"
      }
    ]);


    try {
      setLoading(true)

      const response =
        await regenerateEmail(
          draftId,
          sessionID,
          appliedDetails
        );

      console.log("Regenerate response:");
      console.log(response.data);
      console.log(response.data.meeting_metadata);

      setMessages(prev => [
        ...prev,
        {
          role: "assistant",
          type: "email",
          draft_id: draftId,
          email_id: response.data.email_id,
          subject: response.data.subject,
          body: response.data.body,
          meeting_metadata: response.data.meeting_metadata
        }
      ]);

    } catch (error) {

      console.error(error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          type: "chat",
          content: "Failed to Regenerate Response.",
        },
      ]);

    }
    finally {
      setLoading(false);
    }
  };



  const handleEmailSend = async (
    draftId: number,
    appliedDetails: EmailMeetingDetails
  ) => {

    setMessages(prev => [
      ...prev,
      {
        role: "user",
        content: "Send Email"
      }
    ]);

    try {

      setLoading(true)

      const response = await sendEmail(
        draftId,
        sessionID,
        appliedDetails
      );

      setMessages(prev => [
        ...prev,
        {
          role: "assistant",
          type: "chat",
          content: response.data.answer
        }
      ]);

    } catch (error) {

      console.error(error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          type: "chat",
          content: "Failed to Send Email",
        },
      ]);

    }
    finally {
      setLoading(false)
    }
  };


  const handleZoomToggle = (
    checked: boolean
  ) => {

    const now = new Date();

    const defaultDate =
      now.toISOString().split("T")[0];

    const defaultTime =
      now.toTimeString().slice(0, 5);

    setFormDetails(prev => ({
      ...prev,
      requires_meeting_link: checked,

      date:
        checked && !prev.date
          ? defaultDate
          : prev.date,

      time:
        checked && !prev.time
          ? defaultTime
          : prev.time
    }));
  };



  const meetingPreview = buildMeetingPreview();

  const renderedBody =
    body.includes("[[MEETING_DETAILS]]")
      ? body.replace(
        "[[MEETING_DETAILS]]",
        meetingPreview
      )
      : body;

  return (
    <div className="space-y-3 w-full">

      <div>
        <span className="font-semibold text-sm">
          To:
        </span>{" "}
        <span className="text-xs">
          {email_id}
        </span>

      </div>

      <div>
        <span className="font-semibold text-sm">
          Subject:
        </span>{" "}
        <span className="text-xs">
          {subject}
        </span>

      </div>

      <div className="whitespace-pre-wrap text-xs leading-relaxed">
        <ReactMarkdown>
          {renderedBody}
        </ReactMarkdown>
      </div>

      <div className="flex gap-2 pt-2">

        <button
          onClick={() =>
            handleRegenerate(draft_id, formDetails)
          }
          className="
            px-3
            py-1.5
            rounded-lg
            bg-gray-200
            hover:bg-gray-300
            text-sm
            transition
            cursor-pointer
          "
        >
          Regenerate
        </button>


        <button
          className="
              px-3
              py-1.5
              rounded-lg
              bg-gray-200
              hover:bg-gray-300
              text-sm
              transition
              cursor-pointer
            "
          onClick={() =>
            setShowDetails(!showDetails)
          }
        >
          {showDetails
            ? "Hide Details"
            : "Add Details"}
              </button>
                
                
              <button
                onClick={() =>
                  handleEmailSend(
                    draft_id,
                    appliedDetails
                  )
                }
                className="
                  px-3
                  py-1.5
                  rounded-lg
                  bg-blue-600
                  text-white
                  hover:bg-blue-700
                  text-sm
                  transition
                  cursor-pointer
                "
              >
                Send
              </button>
              
            </div>
              
            {showDetails && (
        <div
          className="
            mt-3
            p-4
            border
            border-gray-300
            rounded-xl
            bg-gray-50
            space-y-4
          "
        >
        
          {/* Zoom Checkbox */}
            
          <div className="flex items-center gap-3">
            <input
              id="zoom-meeting"
              type="checkbox"
              checked={formDetails.requires_meeting_link}
              onChange={(e) =>
                handleZoomToggle(
                  e.target.checked
                )
              }
              className="
                h-4
                w-4
                cursor-pointer
              "
            />
      
            <label
              htmlFor="zoom-meeting"
              className="
                text-sm
                font-medium
                cursor-pointer
                select-none
              "
            >
              Add Zoom Meeting
            </label>
          </div>
            
          {/* Date + Time */}
            
          <div className="grid grid-cols-2 gap-3">
            
            <div>
              <label
                htmlFor="meeting-date"
                className="
                  block
                  text-sm
                  font-medium
                  mb-1
                  cursor-pointer
                "
              >
                Date
              </label>
            
              <input
                id="meeting-date"
                type="date"
                value={formDetails.date}
                onChange={(e) =>
                  setFormDetails({
                    ...formDetails,
                    date: e.target.value,
                  })
                }
                className="
                  w-full
                  rounded-lg
                  border
                  border-gray-300
                  px-3
                  py-2
                  text-sm
                  cursor-pointer
                  focus:outline-none
                  focus:ring-2
                  focus:ring-blue-500
                  focus:border-blue-500
                "
              />
            </div>
              
            <div>
              <label
                htmlFor="meeting-time"
                className="
                  block
                  text-sm
                  font-medium
                  mb-1
                  cursor-pointer
                "
              >
                Time
              </label>
              
              <input
                id="meeting-time"
                type="time"
                value={formDetails.time}
                onChange={(e) =>
                  setFormDetails({
                    ...formDetails,
                    time: e.target.value,
                  })
                }
                className="
                  w-full
                  rounded-lg
                  border
                  border-gray-300
                  px-3
                  py-2
                  text-sm
                  cursor-pointer
                  focus:outline-none
                  focus:ring-2
                  focus:ring-blue-500
                  focus:border-blue-500
                "
              />
            </div>
              
          </div>
              
          {/* Comments */}
              
          <div>
            <label
              htmlFor="meeting-comments"
              className="
                block
                text-sm
                font-medium
                mb-1
                cursor-pointer
              "
            >
              Additional Comments
            </label>
              
            <textarea
              id="meeting-comments"
              rows={4}
              value={formDetails.comments}
              onChange={(e) =>
                setFormDetails({
                  ...formDetails,
                  comments: e.target.value,
                })
              }
              placeholder="Any extra information to include..."
              className="
                w-full
                rounded-lg
                border
                border-gray-300
                px-3
                py-2
                text-sm
                resize-y
                focus:outline-none
                focus:ring-2
                focus:ring-blue-500
                focus:border-blue-500
              "
            />
          </div>
            
          {/* Apply Button */}
            
          <button
            onClick={handleApplyChanges}
            className="
              w-full
              rounded-lg
              bg-blue-600
              px-4
              py-2
              text-sm
              font-medium
              text-white
              hover:bg-blue-700
              transition
              cursor-pointer
            "
          >
            Apply Changes
          </button>
            
        </div>
)}
    </div>
  );
}