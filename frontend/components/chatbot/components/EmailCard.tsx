"use client";

import { useId, useState } from "react";
import ReactMarkdown from "react-markdown";

import { Dispatch, SetStateAction } from "react";

import { Plus, Minus } from "lucide-react";

import { Message } from "../types/chat";

import EmailAddressInput from "./email_card_comp/EmailAdressInput";
import EmailAdressDropdown from "./email_card_comp/EmailAdressDropdown";

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
  draft_id: string;
  email_ids: string[];
  subject: string;
  body: string;
  sessionID: string;
  meeting_metadata?: MeetingMetadata;
  selected_email: string;
  cc_emails: string[];
  bcc_emails: string[];
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
  email_ids,
  subject,
  body,
  meeting_metadata,
  selected_email,
  setLoading,
  setMessages,
  sessionID,
  cc_emails,
  bcc_emails

}: EmailCardProps) {

  // Generate a unique ID for the component instance
  const uniqueId = useId();

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

  const [selectedEmail, setSelectedEmail] = useState(selected_email);


  const [ccEmails, setCcEmails] = useState<string[]>(cc_emails ?? []);
  const [bccEmails, setBccEmails] = useState<string[]>(bcc_emails ?? []);

  const [showCC, setShowCC] = useState((cc_emails ?? []).length > 0);
  const [showBCC, setShowBCC] = useState((bcc_emails ?? []).length > 0);
  
  const handleApplyChanges = () => {
    setAppliedDetails(formDetails);
    setShowDetails(false);
  };


  // Function to format time from 24-hour format to 12-hour format with AM/PM
  const formatTime = (time: string) => {
  if (!time) return "";

  const [hours, minutes] = time
    .split(":")
    .map(Number);

  const period = hours >= 12 ? "PM" : "AM";

  const formattedHours =
    hours % 12 || 12;

  return `${formattedHours}:${minutes
    .toString()
    .padStart(2, "0")} ${period}`;
  };


  // Function to build the meeting preview string based on appliedDetails
  const buildMeetingPreview = () => {
    const lines: string[] = [];

    if (appliedDetails.date) {
      lines.push(
        `- Date: ${appliedDetails.date}`
      );
    }

    if (appliedDetails.time) {
      lines.push(
          `- Time: ${formatTime(appliedDetails.time)}`
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


  // Function to handle the regeneration of the email draft_id
  const handleRegenerate = async () => {



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
          draft_id,
          sessionID,
          appliedDetails,
          subject,
          body,
          email_ids,
          selectedEmail,
          ccEmails,
          bccEmails
        );

      console.log("Regenerate response:");
      console.log(response.data);
      console.log(response.data.meeting_metadata);

      setMessages(prev => [
        ...prev,
        {
          role: "assistant",
          type: "email",

          draft_id: draft_id,

          email_ids: response.data.email_ids,

          subject: response.data.subject,
          body: response.data.body,

          meeting_metadata: response.data.meeting_metadata,

          selected_email: response.data.selected_email,

          cc_emails: response.data.cc_emails,

          bcc_emails: response.data.bcc_emails,
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


  // Function to handle sending the email with the applied details
  const handleEmailSend = async () => {

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
        draft_id,
        sessionID,
        appliedDetails,
        subject,
        body,
        selectedEmail,
        ccEmails,
        bccEmails
      );

      setMessages(prev => [
        ...prev,
        {
          role: "assistant",
          type: "chat",
          content: response.data.message
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

  // Function to handle the toggle of the Zoom meeting checkbox
  // If checked, it sets the date and time to the current date and time if they are not already set.
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


  // Generate unique IDs for the form elements to ensure accessibility and avoid conflicts 
  const zoomCheckboxId =  `${uniqueId}-zoom-meeting`;

  const meetingDateId =    `${uniqueId}-meeting-date`;

  const meetingTimeId =    `${uniqueId}-meeting-time`;

  const meetingCommentsId =    `${uniqueId}-meeting-comments`;



  const meetingPreview = buildMeetingPreview();

  const renderedBody =
    body.includes("[[MEETING_DETAILS]]")
      ? body.replace(
        "[[MEETING_DETAILS]]",
        meetingPreview
      )
      : body;

  return (
    <div className="flex-1 space-y-2.5">

      <EmailAdressDropdown
          emailIds={email_ids}
          selectedEmail={selectedEmail}
          setSelectedEmail={setSelectedEmail}
       />

      {/* CC */}

      {showCC ? (
          <EmailAddressInput
              label="CC"
              placeholder="Press Enter to add CC emails"
              emails={ccEmails}
              setEmails={setCcEmails}
          />
      ) : (
          <div className="ml-20">
              <button
                  type="button"
                  onClick={() => setShowCC(true)}
                  className="
                      flex
                      items-center
                      gap-1
                      text-xs
                      font-medium
                      text-blue-600
                      hover:text-blue-700
                      transition
                      cursor-pointer
                  "
              >
                  <Plus size={14} />
                  Add CC
              </button>
          </div>
      )}

      {/* BCC */}

      {showBCC ? (
          <EmailAddressInput
              label="BCC"
              placeholder="Press Enter to add BCC email"
              emails={bccEmails}
              setEmails={setBccEmails}
          />
      ) : (
          <div className="ml-20">
              <button
                  type="button"
                  onClick={() => setShowBCC(true)}
                  className="
                      flex
                      items-center
                      gap-1
                      text-xs
                      font-medium
                      text-blue-600
                      hover:text-blue-700
                      transition
                      cursor-pointer
                  "
              >
                  <Plus size={14} />
                  Add BCC
              </button>
          </div>
      )}


      <div className="flex items-center gap-2">
        <span className="w-16 shrink-0 text-xs font-semibold text-gray-700">
          Subject:
        </span>{" "}
        <span className="flex-1 text-xs text-gray-800 leading-6">
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
            handleRegenerate()
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
                  handleEmailSend()
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
              id={zoomCheckboxId}
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
              htmlFor={zoomCheckboxId}
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
                htmlFor={meetingDateId}
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
                id={meetingDateId}
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
                htmlFor={meetingTimeId}
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
                id={meetingTimeId}
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
              htmlFor={meetingCommentsId}
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
              id={meetingCommentsId}
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